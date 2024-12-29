from flask import render_template
from flask_login import current_user


def render_template_navbar(template: str, **context) -> str:
    if not context: context = dict()
    if current_user and hasattr(current_user, 'username'):
        context['navbar_info'] = f'logged in as {current_user.username}'
    else:
        context['navbar_info'] = 'not logged in'
    return render_template(template, **context)


if __name__ == "__main__":
    pass
