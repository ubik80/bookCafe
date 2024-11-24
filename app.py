from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_toastr import Toastr
from functools import wraps
from book_cafe.db_models import db, Role, Role_User, User, Book, initialize_database


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///bookcafe"
app.config["SECRET_KEY"] = "abc"
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
toastr = Toastr(app)


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_role(required_role):
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_role = Role.get_role("User")
        new_user = User.add_new(username=request.form.get("username"), password=request.form.get("password"))
        db.session.commit()
        Role_User.add_new(role_id = user_role.id, user_id = new_user.id)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.get_user_by_name(username=request.form.get("username"))
        if user and user.check_password(request.form.get("password")):
            login_user(user)
            flash("You are logged in.")
            return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are logged out.")
    return redirect(url_for("home"))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add_book", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_book():
    if request.method == "POST":
        Book.add_new(
            title=request.form.get("title"),
            author=request.form.get("author"),
            description=request.form.get("description"),
            user_id=current_user.id)
        db.session.commit()
        flash("Book added to library.")
        return redirect(url_for("add_book"))
    return render_template("add_book.html")


@app.route("/delete_book/<id>", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def delete_book(id):
    book = Book.get_book_by_id(id)
    book.delete()
    db.session.commit()
    flash("Book deleted from library.")
    return redirect(url_for("find_book"))


@app.route("/find_book", methods=["GET", "POST"])
@login_required
def find_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        sort_by = request.form.get("sort_by")
        session['title'] = title or ""
        session['author'] = author or ""
        session['sort_by'] = sort_by or "title"
        return redirect(url_for("find_book"))
    title = session.get("title") or ""
    author = session.get("author") or ""
    sort_by = session.get("sort_by") or "title"
    books = query_books(author, title, sort_by)
    return render_template("find_book.html", author=author, title=title, sort_by=sort_by, books=books)


def query_books(author, title, sort_by):
    books = Book.get_books_by_author_title(author=author, title=title, sort_by=sort_by)
    books = [{'title': b.title, 'author': b.author, 'description': b.description[:100], 'book_id': b.id} for b in books]
    return books


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initialize_database()
    app.run(debug=True)
