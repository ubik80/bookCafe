from book_cafe.app_logger import logger
from book_cafe.db_objects import User, Book, Role, Role_User, db
from book_cafe.exceptions import sql_alchemy_exception


@sql_alchemy_exception()
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


@sql_alchemy_exception()
def query_books(author: str, title: str, sort_by: str) -> list[dict]:
    books = Book.get_books_by_author_title(author=author, title=title, sort_by=sort_by)
    books = [{'title': b.title, 'author': b.author, 'description': b.description[:100], 'book_id': b.id} for b in books]
    return books


if __name__ == "__main__":
    pass
