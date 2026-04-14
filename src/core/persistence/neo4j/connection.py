from neomodel import config

def init_db_connection(url: str):
    config.DATABASE_URL = url