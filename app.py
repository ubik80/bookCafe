from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, user_logged_in
from flask_migrate import Migrate
from flask_toastr import Toastr
from flask import g
from book_cafe.db_models import db, Role, Role_User, User, Book, initialize_database


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///bookcafe"
app.config["SECRET_KEY"] = "abc"
app.config['SECURITY_REGISTERABLE'] = True
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
toastr = Toastr(app)


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_role = Role.query.filter(Role.role_name == "User").first()
        new_user = User.add_new(username=request.form.get("username"), password=request.form.get("password"))
        db.session.commit()
        Role_User.add_new(role_id = user_role.id, user_id = new_user.id)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and user.check_password(request.form.get("password")):
            login_user(user)
            g.user_id = user.id
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
#@roles_required('Admin')
def add_book():
    if request.method == "POST":
        Book.add_new(title=request.form.get("title"), author=request.form.get("author"), description=request.form.get("description"), user_id=g.user_id)
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
    if sort_by == "author":
        books = (Book.query.
                 filter(Book.title.like(f'%{title}%') & Book.author.like(f'%{author}%'))
                 .order_by(Book.author.asc())
                 .all())
    else:
        books = (Book.query.
                 filter(Book.title.like(f'%{title}%') & Book.author.like(f'%{author}%'))
                 .order_by(Book.title.asc())
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
    with app.app_context():
        db.create_all()
        initialize_database()
    app.run(debug=True)
