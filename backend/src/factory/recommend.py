from typing import  Union
from .utils import load_df_top_news, load_users_list
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import joblib
import os

class Recommend():
    def __init__(self, user_id: Union[str, None] = None, news_id: Union[str, None]= None) -> None:
        self.user_id = user_id
        self.news_id = news_id
        self.dataset_top_news = load_df_top_news()
        self.user_id_to_index = load_users_list()
        self.items_df = pd.read_parquet('src/data/processed/items.parquet')
        self.tfidf_matrix = joblib.load('src/model/tfidf_matrix.pkl')
        self.nn_model = joblib.load('src/model/nn_model.pkl')


    def recommendNews(self):
        return self.__recommend_news_based(self.news_id)

    def recommendMainPage(self):
        return self.__recommend_main_page(self.user_id)


    def __recommend_main_page(self, user_id = None, top_n=10, weight_cf=0.5, weight_cb=0.5):
        """
        Combina as recomendações de Collaborative Filtering (CF) e Content-Based (CB) usando KNN.
        Para cada usuário, são obtidas as recomendações CF e, para o histórico do usuário,
        utiliza-se o KNN para buscar itens similares. Os scores de ambos os métodos são
        combinados de forma ponderada para gerar o ranking final.
        """
        # Recomendações baseadas em CF
        recs_cf = self.__recommend_user_based(user_id, top_n=top_n*2)
        
        # Obter o histórico do usuário a partir do dataset de treino
        user_history = []
        train_df = pd.read_parquet('src/data/processed/interacoes_scored.parquet')

        df_user = train_df[train_df['userId'] == user_id]
        for hist in df_user['itemId']:
            user_history.append(hist)
        
        
        # Recomendações baseadas em conteúdo utilizando KNN
        # Para cada item do histórico, buscamos os itens mais similares
        score_cb = {}
        for item in user_history:
            similar_items = self.__recommend_news_based(item, top_n=10)  # Obtemos os 10 itens mais similares para cada item
            for rec in similar_items:
                # Ignoramos itens já consumidos
                if rec in user_history:
                    continue
                # Acumula uma contagem que pode representar a força do sinal
                score_cb[rec] = score_cb.get(rec, 0) + 1

        # Ordena os itens recomendados pelo conteúdo com base no score acumulado
        recs_cb = [item for item, score in sorted(score_cb.items(), key=lambda x: x[1], reverse=True)][:top_n*2]
        
        # Combinação simples: somamos os pesos das recomendações CF e CB
        score_dict = {}
        for item in recs_cf:
            score_dict[item] = score_dict.get(item, 0) + weight_cf
        for item in recs_cb:
            score_dict[item] = score_dict.get(item, 0) + weight_cb
            
        # Ordena os itens combinados e retorna os top_n
        ranked_items = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
        return [item for item, score in ranked_items][:top_n]


    def __recommend_user_based(self, user_id=None, top_n=10, n_neighbors=2000):
        """
        Recomenda itens para um usuário utilizando vizinhos mais próximos (CF via NearestNeighbors).
        Para um dado usuário, busca os n vizinhos mais próximos com base na interação,
        acumula os itens que eles consumiram (excluindo os já consumidos pelo usuário) e os ordena por similaridade agregada.
        """
        if user_id not in self.user_id_to_index:
            return list(self.__recommend_popular_news(top_n)['itemId'])
        
        unique_items = pd.read_parquet('src/data/processed/top_news.parquet', columns=['itemId'])['itemId'].tolist()
        interaction_matrix = joblib.load('src/model/interaction_matrix.pkl')

        user_idx = self.user_id_to_index[user_id]
        nn_model_cf = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=n_neighbors, n_jobs=-1)
        nn_model_cf.fit(interaction_matrix)
        # Buscar os vizinhos mais próximos para o usuário (a consulta retorna o próprio usuário com distância 0)
        distances, indices = nn_model_cf.kneighbors(interaction_matrix[user_idx], n_neighbors=n_neighbors)
        distances = distances.flatten()
        indices = indices.flatten()
        
        # Converter a distância em similaridade (1 - distância, pois a distância cosseno varia entre 0 e 1)
        # E acumular os itens dos vizinhos, ignorando os itens já consumidos pelo usuário
        user_items = set(interaction_matrix[user_idx].nonzero()[1])
        rec_scores = {}
        
        for neighbor_idx, dist in zip(indices, distances):
            # Ignorar o próprio usuário
            if neighbor_idx == user_idx:
                continue
            similarity = 1 - dist  # Similaridade: quanto menor a distância, maior a similaridade
            neighbor_items = interaction_matrix[neighbor_idx].nonzero()[1]
            for item in neighbor_items:
                if item in user_items:
                    continue  # Ignorar itens já consumidos
                rec_scores[item] = rec_scores.get(item, 0) + similarity

        # Ordenar os itens por pontuação decrescente e retornar os top_n (convertendo os índices para IDs reais)
        ranked_items = sorted(rec_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_item_ids = [unique_items[idx] for idx, score in ranked_items[:top_n]]
        
        return recommended_item_ids


    def __recommend_popular_news(self, top_n=10, weight_recency=0.3, weight_visits=0.4, weight_time=0.3):
        """
        Calcula um score de popularidade para cada notícia com base na data de lançamento (Issued),
        número de visitas e tempo na página.
        
        Parâmetros:
        - df: DataFrame contendo as colunas 'Issued', 'visits' e 'timeOnPage'.
        - top_n: quantidade de notícias mais populares a serem retornadas.
        - weight_recency: peso para o fator de recência.
        - weight_visits: peso para o número de visitas.
        - weight_time: peso para o tempo na página.
        
        Retorna:
        - DataFrame com as top_n notícias ordenadas pela popularidade.
        """

        # carregar df_top_news
        df = self.dataset_top_news

        # Converter a coluna 'Issued' para datetime, se ainda não estiver
        df['issued'] = pd.to_datetime(df['issued'], utc=True)
        
        # Usar a data atual ou a data máxima do DataFrame como referência para recência
        reference_date = reference_date = df['issued'].max()  # ou: df['Issued'].max()
        df['days_since'] = (reference_date - df['issued']).dt.days
        
        # Calcular um score de recência: quanto menor os dias desde a emissão, maior o score
        # Usamos 1 / (dias + 1) para evitar divisão por zero
        df['recency_score'] = 1 / (df['days_since'] + 1)
        
        # Normalizar as colunas 'visits' e 'timeOnPage' para o intervalo [0,1]
        df['visits_norm'] = (df['visits'] - df['visits'].min()) / (df['visits'].max() - df['visits'].min() + 1e-9)
        df['timeOnPage_norm'] = (df['timeOnPage'] - df['timeOnPage'].min()) / (df['timeOnPage'].max() - df['timeOnPage'].min() + 1e-9)
        
        # Calcular o score de popularidade combinando as métricas com os pesos definidos
        df['popularity_score'] = (weight_recency * df['recency_score'] +
                                weight_visits * df['visits_norm'] +
                                weight_time * df['timeOnPage_norm'])
        
        # Ordenar o DataFrame com base no score de popularidade em ordem decrescente
        df_popular = df.sort_values('popularity_score', ascending=False)
        
        return df_popular[:top_n]


    def __recommend_news_based(self, item_id, top_n=10):
        """
        Dado um ID de item, retorna os top_n itens mais similares utilizando TF-IDF e NearestNeighbors.
        """
        items_df = self.items_df
        tfidf_matrix = self.tfidf_matrix
        nn_model = self.nn_model

        if len(items_df[items_df['page'] == item_id]) == 0: 
            return []
        
        # Obter o índice correspondente no tfidf_matrix
        item_idx = items_df[items_df['page'] == item_id]
        query_vector = tfidf_matrix[item_idx.index]
        
        # Buscar os vizinhos mais próximos (n_neighbors inclui o próprio item, por isso solicitamos top_n+1)
        distances, indices = nn_model.kneighbors(query_vector, n_neighbors=top_n+1)
        
        # Ignorar o primeiro resultado (o próprio item) e mapear para os IDs dos itens
        similar_indices = indices.flatten()[1:]
        similar_item_ids = [items_df.index[i] for i in similar_indices]


        return items_df[items_df.index.isin(similar_item_ids)]['page'].values.tolist()