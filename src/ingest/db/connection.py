from neomodel import config

def init_db_connection():
    config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'