from redis import Redis
import json


class RedisConnector:
    def __init__(self, host: str, port: int, db: int):
        self.redis_client = Redis(host=host, port=port, db=db)

    def set(self, key: str, value: bytes | str):
        self.redis_client.set(key, value)

    def get(self, key: str) -> dict:
        return json.loads(self.redis_client.get(key).decode('utf-8')) if self.redis_client.get(key) else None

    def delete(self, key: str):
        self.redis_client.delete(key)

    def expire(self, key: str, time: int):
        self.redis_client.expire(key, time)