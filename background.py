import time

from flask import Flask

from book_cafe.db_objects import db
from book_cafe.logging import logger
from book_cafe.user_management import reset_failed_login_attempts, logout_inactive_users
from confidential import SECRET_KEY
from configuration import CYCLIC_TASKS_FREQUENCY_SECONDS, DB_CONNECTION_STRING, DEBUG_MODE_ON


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_CONNECTION_STRING
app.config["SECRET_KEY"] = SECRET_KEY
db.init_app(app)


if __name__ == "__main__":
    logger.info(f"-------- background started --------")
    while True:
        with app.app_context():
            reset_failed_login_attempts(db.session)
            logout_inactive_users(db.session)
        if DEBUG_MODE_ON: logger.info(f"Cyclic tasks executed")
        time.sleep(CYCLIC_TASKS_FREQUENCY_SECONDS)
