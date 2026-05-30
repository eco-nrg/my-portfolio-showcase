from django.conf import settings
from redis import ConnectionPool, Redis


class RedisProvider:
    connection_pool: ConnectionPool = ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    @staticmethod
    def get_connection() -> Redis:
        return Redis.from_pool(connection_pool=RedisProvider.connection_pool)
