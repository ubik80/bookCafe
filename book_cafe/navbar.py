import time
from datetime import datetime

from flask import render_template, Blueprint, Response
from flask_login import current_user


def render_template_navbar(template: str, **context) -> str:
    if not context: context = dict()
    if current_user and hasattr(current_user, 'username'):
        context['navbar_info'] = f'logged in as {current_user.username}'
    else:
        context['navbar_info'] = 'not logged in'
    return render_template(template, **context)


navbar_stream = Blueprint('navbar_stream', __name__, template_folder='templates')


@navbar_stream.route('/navbar_stream')
def stream():
    def event_stream():
        while True:
            yield "data:" + f"{datetime.now()}" + "\n\n"
            time.sleep(5)

    return Response(event_stream(), mimetype='text/event-stream')


if __name__ == "__main__":
    pass
