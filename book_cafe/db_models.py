from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_security import UserMixin, RoleMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Role_User(db.Model):
    __tablename__ = 'role_user'
    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))

    @staticmethod
    def add_new(role_id, user_id):
        new_role_user = Role_User(role_id = role_id, user_id = user_id)
        db.session.add(new_role_user)
        return new_role_user


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    role_name = db.Column(db.String(80), unique=True)
    role_user = db.relationship('Role_User', backref='role_user',)

    @staticmethod
    def add_new(role_name):
        new_role = Role(role_name=role_name)
        db.session.add(new_role)
        return new_role


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, index=True, nullable=False)
    password = db.Column(db.String(164), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    active = db.Column(db.Boolean())
    books = db.relationship('Book', backref='book',)
    roles = db.relationship('Role_User', backref='role',)

    @staticmethod
    def add_new(username, password):
        new_user = User(username=username)
        new_user.set_password(p=password)
        db.session.add(new_user)
        return new_user

    def set_password(self, p):
        self.password = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password, p)


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), index=True, nullable=False)
    author = db.Column(db.String(50), index=True, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    user_created = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.Index('title_author_index', 'title', 'author'),)

    @staticmethod
    def add_new(title, author, description, user_id):
        new_book = Book(title=title, author=author, description=description, user_id=user_id)
        db.session.add(new_book)
        return new_book


def initialize_database():
    if not Role.query.filter(Role.role_name == 'Admin').first():
        Role.add_new(role_name='Admin')
    if not Role.query.filter(Role.role_name == 'User').first():
        Role.add_new(role_name='User')
    admin_user = User.query.filter(User.username == 'Admin').first()
    if admin_user:
        admin_role = Role.query.filter(Role.role_name == "Admin").first()
        role_user_admin = Role_User.query.filter((Role_User.user_id == admin_user.id) & (Role_User.role_id == admin_role.id)).first()
        if not role_user_admin:
            Role_User.add_new(role_id=admin_role.id, user_id=admin_user.id)
    db.session.commit()


if __name__ == "__main__":
    pass
