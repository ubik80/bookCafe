from datetime import datetime
from sys import getsizeof

from flask import Flask, Response, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_toastr import Toastr

from book_cafe.db_functions import query_books, initialize_database
from book_cafe.db_objects import Role, Role_User, User, Book, db
from book_cafe.forms import Login_Form, Register_Form, Add_Book_Form, Find_Book_Form
from book_cafe.logging import logger
from book_cafe.navbar import render_template_navbar, navbar_news_stream, set_navbar_news
from book_cafe.reddis import redis_client
from book_cafe.user_management import role_required, refresh_user, login_manager
from confidential import SECRET_KEY
from configuration import DB_CONNECTION_STRING, MAX_FAILED_LOGIN_ATTEMPTS, DEBUG_MODE_ON, HOST_IP

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_CONNECTION_STRING
app.config["SECRET_KEY"] = SECRET_KEY
db.init_app(app)
migrate = Migrate(app, db)
redis_client.init_app(app)
toastr = Toastr(app)


app.register_blueprint(navbar_news_stream)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = Register_Form()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        existing_user = User.get_user_by_name(username)
        if existing_user:
            flash("Username already in use.")
            return render_template_navbar("sign_up.html", form=form)
        user_role = Role.get_role("User")
        new_user = User.add_new(username=username, password=password)
        db.session.commit()
        Role_User.add_new(role_id=user_role.id, user_id=new_user.id)
        db.session.commit()
        flash("New account created.")
        logger.info(f"Account for user {username} created.")
        return redirect(url_for("login"))
    return render_template_navbar("sign_up.html", form=form)


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
        elif user.failed_login_attempts > MAX_FAILED_LOGIN_ATTEMPTS:
            flash("Too many failed login attempts")
        elif user.check_password(password):
            login_user(user)
            user.is_logged_in = True
            db.session.commit()
            flash("You are logged in.")
            logger.info(f"User {username} logged in.")
            set_navbar_news(f'{username} logged in.')
            return redirect(url_for("find_book"))
        else:
            user.failed_login_attempts += 1
            user.last_failed_login_attempt = datetime.now()
            db.session.commit()
            logger.info(f"Unsuccessful login attempt for user {username}.")
    return render_template_navbar("login.html", form=form)


@app.route("/logout")
@login_required
def logout() -> Response:
    logger.info(f'{current_user.username} logged out.')
    set_navbar_news(f'{current_user.username} logged out.')
    current_user.is_logged_in = False
    db.session.commit()
    logout_user()
    session.clear()
    flash("You are logged out.")
    return redirect(url_for("login"))


@app.route("/")
@refresh_user()
def home() -> Response:
    return redirect(url_for("find_book"))


@app.route("/add_book", methods=["GET", "POST"])
@login_required
@role_required("Admin")
@refresh_user()
def add_book():
    form = Add_Book_Form()
    if form.validate_on_submit():
        existing_book = Book.get_books_by_author_title(form.author.data, form.title.data)
        if existing_book:
            flash("Book already in library.")
            return render_template_navbar("add_book.html", form=form)
        binary_pic_data = None
        if form.cover_picture.data:
            binary_pic_data = form.cover_picture.data.read()
            if getsizeof(binary_pic_data) > 500 * 1024:
                flash("Cover picture size is too large.")
                return render_template_navbar("add_book.html", form=form)
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
    return render_template_navbar("add_book.html", form=form)


@app.route("/delete_book/<id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
@refresh_user()
def delete_book(id: int) -> Response:
    book = Book.get_book_by_id(id)
    book.delete()
    db.session.commit()
    flash("Book deleted from library.")
    logger.info(f"Book \'{book.title}\' deleted.")
    return redirect(url_for("find_book"))


@app.route("/find_book", methods=["GET", "POST"])
@login_required
@refresh_user()
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
    return render_template_navbar("find_book.html", books=books, form=form)


if __name__ == "__main__":
    logger.info(f"-------- app started --------")
    with app.app_context():
        db.create_all()
        initialize_database()
        login_manager.init_app(app)
    app.run(debug=DEBUG_MODE_ON, host=HOST_IP, threaded=True)
