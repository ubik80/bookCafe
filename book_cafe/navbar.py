import time
from datetime import datetime

from flask import render_template, Blueprint, Response
from flask_login import current_user

from book_cafe.exceptions import reddis_exception
from book_cafe.redis import redis_client
from constants import REDIS_KEY_NAVBAR_NEWS, REDIS_KEY_NAVBAR_NEWS_DATE


@reddis_exception()
def render_template_navbar(template: str, **context) -> str:
    if not context: context = dict()
    if current_user and hasattr(current_user, 'username'):
        context['navbar_info'] = f'You are logged in as {current_user.username}.'
    else:
        context['navbar_info'] = 'You are not logged in'
    return render_template(template, **context)


navbar_news_stream = Blueprint('navbar_stream', __name__, template_folder='templates')


@navbar_news_stream.route('/navbar_stream')
@reddis_exception()
def stream_navbar_news():
    def event_stream():
        monkeys = ['🍅', '🥦']
        i = 0
        while True:
            news = redis_client.get(REDIS_KEY_NAVBAR_NEWS)
            yield "data:" + f"[{news}] " + monkeys[i] + "\n\n"
            i = 1 if i == 0 else 0
            time.sleep(5)
    return Response(event_stream(), mimetype='text/event-stream')


@reddis_exception()
def set_navbar_news(news):
    redis_client.set(REDIS_KEY_NAVBAR_NEWS, news)
    redis_client.set(REDIS_KEY_NAVBAR_NEWS_DATE, str(datetime.now()))


if __name__ == "__main__":
    pass
