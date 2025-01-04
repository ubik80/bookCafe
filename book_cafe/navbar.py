import time
from flask import render_template, Blueprint, Response
from flask_login import current_user

from book_cafe.reddis import redis_client


def render_template_navbar(template: str, **context) -> str:
    if not context: context = dict()
    if current_user and hasattr(current_user, 'username'):
        context['navbar_info'] = f'You are logged in as {current_user.username}.'
    else:
        context['navbar_info'] = 'You are not logged in'
    return render_template(template, **context)


navbar_stream = Blueprint('navbar_stream', __name__, template_folder='templates')


@navbar_stream.route('/navbar_stream')
def stream():
    def event_stream():
        monkeys = ['🍅', '🥦']
        i = 0
        while True:
            news = redis_client.get('navbar_news')
            yield "data:" + f"[{news}] " +  monkeys[i]  + "\n\n"
            i = 1 if i==0 else 0
            time.sleep(5)
    return Response(event_stream(), mimetype='text/event-stream')


if __name__ == "__main__":
    pass
