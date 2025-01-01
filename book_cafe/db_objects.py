from datetime import datetime, timedelta

from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from configuration import FAILED_LOGINS_WAIT_MINUTES, AUTOMATIC_LOGOUT_INACTIVITY_MINUTES


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Role_User(db.Model):
    __tablename__ = 'role_user'
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), index=True)
    user = relationship("User", back_populates="role_ids")
    role = relationship("Role")

    @staticmethod
    def add_new(role_id: int, user_id: int) -> "Role_User":
        new_role_user = Role_User(role_id=role_id, user_id=user_id)
        db.session.add(new_role_user)
        return new_role_user


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    @staticmethod
    def add_new(role_name: str):
        new_role = Role(name=role_name)
        db.session.add(new_role)
        return new_role

    @staticmethod
    def get_role(role_name: str) -> "Role":
        role = Role.query.filter(Role.name == role_name).first()
        return role


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, index=True, nullable=False)
    password = db.Column(db.String(164), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_authenticated = db.Column(db.Boolean, default=True, nullable=False)
    is_logged_in = db.Column(db.Boolean, default=True, index=True, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, index=True, nullable=False)
    last_failed_login_attempt = db.Column(db.DateTime, default=datetime.now(), index=True, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.now(), index=True, nullable=False)
    role_ids = relationship("Role_User", back_populates="user")

    @staticmethod
    def add_new(username: str, password: str) -> "User":
        new_user = User(username=username)
        new_user.set_password(p=password)
        db.session.add(new_user)
        return new_user

    @staticmethod
    def get_user_by_name(username: str) -> "User":
        user = User.query.filter(User.username == username).first()
        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> "User":
        user = User.query.filter(User.id == user_id).first()
        return user

    @staticmethod
    def get_users_with_failed_logins_to_reset() -> list["User"]:
        older_than = datetime.now() - timedelta(minutes=FAILED_LOGINS_WAIT_MINUTES)
        users = (User.query
                 .filter((User.failed_login_attempts > 0) & (User.last_failed_login_attempt < older_than))
                 .all())
        return users

    @staticmethod
    def get_inactive_users() -> list["User"]:
        inactive_threshold = datetime.now() - timedelta(minutes=AUTOMATIC_LOGOUT_INACTIVITY_MINUTES)
        users = (User.query
                 .filter(User.is_logged_in & (User.last_activity < inactive_threshold))
                 .all())
        return users

    def set_password(self, p: str):
        self.password = generate_password_hash(p)

    def check_password(self, p: str) -> bool:
        return check_password_hash(self.password, p)

    def get_id(self: "User") -> str:
        return str(self.id)

    def has_role(self, required_role: "Role") -> bool:
        roles = [rid.role.name for rid in self.role_ids]
        if required_role in roles: return True
        return False

    def reset_failed_login_attempts(self: "User"):
        self.failed_login_attempts = 0


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, nullable=False)
    author = db.Column(db.String(50), index=True, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    cover_picture = db.Column(db.LargeBinary)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    user_created = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.Index('title_author_index', 'title', 'author'),)

    @staticmethod
    def add_new(title: str, author: str, description: str, user_id: int, cover_picture: db.LargeBinary) -> "Book":
        new_book = Book(title=title, author=author, description=description, user_created=user_id,
                        cover_picture=cover_picture)
        db.session.add(new_book)
        return new_book

    @staticmethod
    def get_book_by_id(book_id: int) -> "Book":
        book = (Book.query.filter(Book.id == book_id)).one()
        return book

    @staticmethod
    def get_books_by_author_title(author: str, title: str, sort_by: str = 'title') -> list["Book"]:
        if sort_by == "author":
            books = (Book.query
                     .filter(Book.title.like(f'%{title}%') & Book.author.like(f'%{author}%'))
                     .order_by(Book.author.asc())
                     .all())
        else:
            books = (Book.query
                     .filter(Book.title.like(f'%{title}%') & Book.author.like(f'%{author}%'))
                     .order_by(Book.title.asc())
                     .all())
        return books

    def delete(self: "Book"):
        db.session.delete(self)


if __name__ == "__main__":
    pass
