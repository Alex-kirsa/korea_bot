from redis.asyncio import Redis

from configreader import config

redis = Redis(
    host=config.redis_host,
    port=config.redis_port,
    db=config.redis_db,
)
