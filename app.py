from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, backref
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_migrate import Migrate
from flask_toastr import Toastr
from datetime import datetime


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///bookcafe"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
toastr = Toastr(app)


with app.app_context():
    db.create_all()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(25), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    books = db.relationship('Book', backref='user',)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    user_created = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(username=request.form.get("username"), password=request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.password == request.form.get("password"):
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
def add_book():
    if request.method == "POST":
        book = Book(
            title=request.form.get("title"),
            author=request.form.get("author"),
            description=request.form.get("description"))
        db.session.add(book)
        db.session.commit()
        flash("Book added to library.")
        return redirect(url_for("add_book"))
    return render_template("add_book.html")


@app.route("/find_book", methods=["GET", "POST"])
@login_required
def find_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        session['title'] = title
        session['author'] = author
        return redirect(url_for("find_book"))
    title = session.get("title") or ""
    author = session.get("author") or ""
    books = query_books(author, title)
    return render_template("find_book.html", author=author, title=title, books=books)


def query_books(author, title):
    books = (Book.query.
             filter(Book.title.like(f'%{title}%') & Book.author.like(f'%{author}%'))
             .all())
    books = [{'title': b.title, 'author': b.author, 'description': b.description[:100], 'book_id': b.id} for b in books]
    return books


@app.route("/delete_book/<id>", methods=["GET", "POST"])
@login_required
def delete_book(id):
    Book.query.filter_by(id=id).delete()
    db.session.commit()
    flash("Book deleted from library.")
    return redirect(url_for("find_book"))


if __name__ == "__main__":
    app.run(debug=True)
