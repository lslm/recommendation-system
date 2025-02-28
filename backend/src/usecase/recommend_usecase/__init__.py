from .dtos import ResponseRecommendationMainPage, ResponseRecommendationNews
from src.factory.recommend import Recommend
from src.factory.utils import get_news_info
from typing import Union


class Recommendation():
    """Classe responsável por realizar a Recomendação de notícias
    """
    def __init__(self, user_id: Union[str, None] = None, news_id: Union[str, None] = None) -> None:
        self.__user_id = user_id
        self.__news_id = news_id
    
    def recommend(self):
        """Realiza a recomendação de notícias

        Returns:
            ResponsePrediction: Resultado da Predição
        """
        if self.__user_id and not self.__news_id:
            ress = Recommend(user_id=self.__user_id).recommendMainPage()
            news = get_news_info(ress)[['page', 'title', 'caption', 'url', 'issued']].to_dict(orient='records')
            return ResponseRecommendationMainPage(noticias=news)

        elif self.__news_id:
            ress = Recommend(news_id=self.__news_id).recommendNews()
            
            current_news = get_news_info(self.__news_id)[['page', 'title', 'caption', 'body', 'url', 'issued']]
            news_related = get_news_info(ress)[['page', 'title', 'caption', 'url', 'issued']].to_dict(orient='records')
            return ResponseRecommendationNews(
                page=current_news['page'].values[0],
                title=current_news['title'].values[0],
                caption=current_news['caption'].values[0],
                body=current_news['body'].values[0],
                url=current_news['url'].values[0],
                issued=current_news['issued'].values[0],
                relatedNews=news_related
            )

        else:
            ress = Recommend().recommendMainPage()
            news = get_news_info(ress)[['page', 'title', 'caption', 'url', 'issued']].to_dict(orient='records')
            return ResponseRecommendationMainPage(noticias=news)