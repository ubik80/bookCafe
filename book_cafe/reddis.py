from flask_redis import FlaskRedis


redis_client = FlaskRedis(decode_responses=True)


if __name__ == "__main__":
    pass