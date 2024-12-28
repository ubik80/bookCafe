import logging
import time
import threading
from logging import handlers
from typing import Callable
from flask import Flask, render_template, Response, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_toastr import Toastr
from functools import wraps
from sys import getsizeof
from book_cafe.db_models import db, Role, Role_User, User, Book
from book_cafe.forms import Login_Form, Register_Form, Add_Book_Form, Find_Book_Form
from datetime import datetime
from configuration import (DB_CONNECTION_STRING, CYCLIC_TASKS_FREQUENCY_SECONDS, ALLOWED_PICTURE_FILE_EXTENSIONS,
                           MAX_FAILED_LOGIN_ATTEMPTS, LOGFILE_NAME, NUM_OF_LOGFILE_BACKUPS, LOGFILES_MAX_BYTES)
from confidential import SECRET_KEY

logger = logging.getLogger(__name__)
handler = handlers.RotatingFileHandler(filename=LOGFILE_NAME, maxBytes=LOGFILES_MAX_BYTES, backupCount=NUM_OF_LOGFILE_BACKUPS)
formater = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_CONNECTION_STRING
app.config["SECRET_KEY"] = SECRET_KEY
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
toastr = Toastr(app)


def role_required(required_role: str) -> Callable:
    def decorator(f: Callable):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_role(required_role):
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.get_user_by_id(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = Register_Form()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        existing_user = User.get_user_by_name(username)
        if existing_user:
            flash("Username already in use.")
            return render_template("sign_up.html", form=form)
        user_role = Role.get_role("User")
        new_user = User.add_new(username=username, password=password)
        db.session.commit()
        Role_User.add_new(role_id=user_role.id, user_id=new_user.id)
        db.session.commit()
        flash("New account created.")
        logger.info(f"Account for user {username} created.")
        return redirect(url_for("login"))
    return render_template("sign_up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login_Form()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get_user_by_name(username=username)
        if not user:
            flash("Register first")
            return redirect(url_for("register"))
        elif user.failed_login_attempts > MAX_FAILED_LOGIN_ATTEMPTS :
            flash("Too many failed login attempts")
        elif user.check_password(password):
            login_user(user)
            flash("You are logged in.")
            logger.info(f"User {username} logged in.")
            return redirect(url_for("find_book"))
        else:
            user.failed_login_attempts += 1
            user.last_failed_login_attempt = datetime.now()
            db.session.commit()
            logger.info(f"Unsuccessful login attempt for user {username}.")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    session.clear()
    flash("You are logged out.")
    logger.info(f"User logged out.")
    return redirect(url_for("login"))


@app.route("/")
def home() -> Response:
    return redirect(url_for("find_book"))


def is_allowed_filename(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PICTURE_FILE_EXTENSIONS


@app.route("/add_book", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_book():
    form = Add_Book_Form()
    if form.validate_on_submit():
        existing_book = Book.get_books_by_author_title(form.author.data, form.title.data)
        if existing_book:
            flash("Book already in library.")
            return render_template("add_book.html", form=form)
        binary_pic_data = None
        if form.cover_picture.data:
            binary_pic_data = form.cover_picture.data.read()
            if getsizeof(binary_pic_data) > 500 * 1024:
                flash("Cover picture size is too large.")
                return render_template("add_book.html", form=form)
        Book.add_new(
            title=form.title.data,
            author=form.author.data,
            description=form.description.data,
            user_id=current_user.id,
            cover_picture=binary_pic_data)
        db.session.commit()
        flash("Book added to library.")
        logger.info(f"Book \'{form.title.data}\' added to library.")
        return redirect(url_for("add_book"))
    return render_template("add_book.html", form=form)


@app.route("/delete_book/<id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def delete_book(id: int) -> Response:
    book = Book.get_book_by_id(id)
    book.delete()
    db.session.commit()
    flash("Book deleted from library.")
    logger.info(f"Book \'{book.title}\' deleted.")
    return redirect(url_for("find_book"))


@app.route("/find_book", methods=["GET", "POST"])
@login_required
def find_book():
    form = Find_Book_Form()
    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        sort_by = form.sort_by.data
        session['title'] = title or ""
        session['author'] = author or ""
        session['sort_by'] = sort_by or "title"
        return redirect(url_for("find_book"))
    form.title.data = session.get("title") or ""
    form.author.data = session.get("author") or ""
    form.sort_by.data = session.get("sort_by") or "title"
    books = query_books(form.author.data, form.title.data, form.sort_by.data)
    return render_template("find_book.html", books=books, form=form)


def query_books(author: str, title: str, sort_by: str) -> list[dict]:
    books = Book.get_books_by_author_title(author=author, title=title, sort_by=sort_by)
    books = [{'title': b.title, 'author': b.author, 'description': b.description[:100], 'book_id': b.id} for b in books]
    return books


def initialize_database():
    if not Role.query.filter(Role.name == 'Admin').first():
        Role.add_new(role_name='Admin')
        logger.info(f"Database initialized - Admin role created.")
    if not Role.query.filter(Role.name == 'User').first():
        Role.add_new(role_name='User')
        logger.info(f"Database initialized - User role created.")
    admin_user = User.query.filter(User.username == 'Admin').first()
    if admin_user:
        admin_role = Role.query.filter(Role.name == "Admin").first()
        role_user_admin = Role_User.query.filter(
            (Role_User.user_id == admin_user.id) & (Role_User.role_id == admin_role.id)).first()
        if not role_user_admin:
            Role_User.add_new(role_id=admin_role.id, user_id=admin_user.id)
            logger.info(f"Database initialized - Admin role assigned to Admin.")
    else:
        logger.info(f"Database initialized - Create Admin user and restart!")
    db.session.commit()


def reset_failed_login_attempts(db_session):
    users = User.get_users_with_failed_logins_to_reset()
    for u in users: u.reset_failed_login_attempts()
    db_session.commit()


def cyclic_thread(db_session):
    with app.app_context():
        while True:
            reset_failed_login_attempts(db_session)
            time.sleep(CYCLIC_TASKS_FREQUENCY_SECONDS)
            #logger.info(f"Cyclic tasks executed")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initialize_database()
    cyc = threading.Thread(target=cyclic_thread, args=[db.session,])
    cyc.start()
    app.run(debug=True)

