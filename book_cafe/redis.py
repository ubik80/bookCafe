from flask_redis import FlaskRedis

from configuration import REDIS_CONNECTION_STRING

redis_client = FlaskRedis(host=REDIS_CONNECTION_STRING, decode_responses=True)


if __name__ == "__main__":
    pass