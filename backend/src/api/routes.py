import logging
from src.usecase.recommend_usecase import ResponseRecommendationMainPage, ResponseRecommendationNews, Recommendation
from src.usecase.users_usecase import ResponseUsers, Users
from fastapi.responses import JSONResponse, Response
from typing import Union
from fastapi.encoders import jsonable_encoder
from src.api.core.dtos import ErrorModel
from fastapi import APIRouter
from http import HTTPStatus

# Configuração básica do logger
logging.basicConfig(
    level=logging.DEBUG, ## ALTERAR PARA INFO QUANDO FINALIZADO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=['News Recommendation'], prefix="/news")

@router.get("/recommendation/")
async def make_prediction(user_id: Union[str, None] = None):
    """
    Handles the prediction request and returns a recommendation response.
    Args:
        user_id (Union[str, None]): The user ID for the recommendation request. This parameter is optional.
    Returns:
        JSONResponse: A JSON response containing the recommendation result or an error message.
    Raises:
        Exception: If an error occurs during the recommendation process, an error response is returned with status code 500.
    """

    try:
        res: ResponseRecommendationMainPage = Recommendation(user_id, None).recommend()
        return JSONResponse(content=jsonable_encoder(res), status_code=HTTPStatus.OK)
    except Exception as ex:
        ex.with_traceback
        error = ErrorModel.from_exception(ex)
        return JSONResponse(content=jsonable_encoder(error), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

@router.get("/recommendation/info/{news_id}")
async def make_prediction(news_id: str):
    """
    Handles the prediction request and returns the recommendation response.

    Args:
        request (RequestRecommendationUnknow): The request object containing the necessary data for making a recommendation.

    Returns:
        JSONResponse: A JSON response containing the recommendation result with a status code of 200 (OK) if successful,
                      or an error message with a status code of 500 (Internal Server Error) if an exception occurs.

    Raises:
        Exception: If an error occurs during the recommendation process, it is caught and an error response is returned.
    """

    try:
        res: ResponseRecommendationNews = Recommendation(news_id=news_id).recommend()
        return JSONResponse(content=jsonable_encoder(res), status_code=HTTPStatus.OK)
    except Exception as ex:
        ex.with_traceback
        error = ErrorModel.from_exception(ex)
        return JSONResponse(content=jsonable_encoder(error), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    
@router.get("/users")
async def get_users():
    """
    Asynchronously retrieves a list of users.
    This function attempts to fetch user data using the Users class and returns
    a JSON response with the user data if successful. If an exception occurs,
    it captures the exception, converts it to an error model, and returns a JSON
    response with the error details.
    Returns:
        JSONResponse: A response object containing the user data or error details.
    """
    
    try:
        res: ResponseUsers = Users().get()
        return JSONResponse(content=jsonable_encoder(res), status_code=HTTPStatus.OK)
    except Exception as ex:
        ex.with_traceback
        error = ErrorModel.from_exception(ex)
        return JSONResponse(content=jsonable_encoder(error), status_code=HTTPStatus.INTERNAL_SERVER_ERROR)