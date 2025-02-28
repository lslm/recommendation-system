from pydantic import BaseModel, Field
from typing import Union


class News(BaseModel):
    page: str = Field(..., title="ID da Notícia")
    title: str = Field(..., title="Título da Notícia")
    caption: str = Field(..., title="Subtitulo da Notícia")
    url: str = Field(..., title="URL da Notícia")
    issued: str = Field(..., title="Data de Publicação da Notícia")


class ResponseRecommendationMainPage(BaseModel):
    noticias: list[News] = Field(..., title="Lista de Notícias Recomendadas")



class ResponseRecommendationNews(BaseModel):
    page: str = Field(..., title="ID da Notícia")
    title: str = Field(..., title="Título da Notícia")
    caption: str = Field(..., title="Subtitulo da Notícia")
    body: str = Field(..., title="Corpo da Notícia")
    url: str = Field(..., title="URL da Notícia")
    issued: str = Field(..., title="Data de Publicação da Notícia")
    relatedNews: list[News] = Field(..., title="Lista de Notícias Relacionadas")
