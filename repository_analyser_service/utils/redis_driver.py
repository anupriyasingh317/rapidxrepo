import os
from redis import Redis

redis_host = os.environ.get("REDIS_HOST")
redis_port = int(os.environ.get("REDIS_PORT"))
redis_password = os.environ.get("REDIS_PASSWORD")

redis_connection = Redis(host=redis_host, 
                         port=redis_port,
                         decode_responses=True,
                         ssl=True,
                         password=redis_password)