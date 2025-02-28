import pandas as pd
import glob


def load_df_top_news():
    df = pd.read_parquet("src/data/processed/top_news.parquet")
    return df


def load_users_list():
    df = pd.read_parquet(r"src/data/processed/user_id.parquet")
    return df['userId'].sample(10).tolist()

def get_news_info(news_id):
    df = pd.read_parquet("src/data/processed/items.parquet")
    if isinstance(news_id, list):
        return df[df['page'].isin(news_id)]	
    return df[df['page'] == news_id]