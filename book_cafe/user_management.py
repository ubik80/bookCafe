from datetime import datetime
from functools import wraps
from typing import Callable

from flask import redirect, url_for
from flask_login import current_user, LoginManager

from book_cafe.db_objects import db, User

login_manager = LoginManager()
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id: int) -> User or None:
    ret = User.get_user_by_id(user_id)
    if not ret.is_logged_in: return None
    return ret


def role_required(required_role: str) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_role(required_role):
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def refresh_user() -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user and hasattr(current_user, 'username'):
                current_user.last_activity = datetime.now()
                db.session.commit()
            return f(*args, **kwargs)
        return wrapped
    return decorator


if __name__ == "__main__":
    pass
