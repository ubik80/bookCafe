import time
from datetime import datetime, timedelta

from flask import Flask

from book_cafe.app_logger import logger
from book_cafe.db_objects import db
from book_cafe.exceptions import sql_alchemy_exception, reddis_exception
from book_cafe.redis import redis_client
from book_cafe.user_management import User
from confidential import SECRET_KEY
from configuration import CYCLIC_TASKS_FREQUENCY_SECONDS, DB_CONNECTION_STRING, DEBUG_MODE_ON
from constants import DATE_TIME_FORMAT, REDIS_KEY_NAVBAR_NEWS, REDIS_KEY_NAVBAR_NEWS_DATE

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_CONNECTION_STRING
app.config["SECRET_KEY"] = SECRET_KEY
redis_client.init_app(app)
db.init_app(app)


@sql_alchemy_exception()
def reset_failed_login_attempts(db_session):
    users = User.get_users_with_failed_logins_to_reset()
    for u in users: u.reset_failed_login_attempts()
    db_session.commit()


@sql_alchemy_exception()
def logout_inactive_users(db_session):
    users = User.get_inactive_users()
    for u in users:
        u.is_logged_in = False
        logger.info(f"user {u.username} logged out because of inactivity.")
    db_session.commit()


@reddis_exception()
def clean_navbar_news():
    news_age_redis = redis_client.get(REDIS_KEY_NAVBAR_NEWS_DATE)
    if not news_age_redis: return
    news_age = datetime.strptime(news_age_redis, DATE_TIME_FORMAT)
    age_threshold = datetime.now() - timedelta(minutes=5)
    if news_age < age_threshold:
        redis_client.set(REDIS_KEY_NAVBAR_NEWS, '')


if __name__ == "__main__":
    message = "-------- background started --------"
    logger.info(message)
    while True:
        with app.app_context():
            reset_failed_login_attempts(db.session)
            logout_inactive_users(db.session)
            clean_navbar_news()
        if DEBUG_MODE_ON:
            message = "Cyclic tasks executed"
            logger.info(message)
        time.sleep(CYCLIC_TASKS_FREQUENCY_SECONDS)
