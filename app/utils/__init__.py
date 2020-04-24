"""
# @Author  wk
# @Time 2020/4/22 10:35

"""
from .cache import *
from .elklog import *
from .httputils import *
from .localcache import *
from .redis import *
from .timeformat import *

from flask import request, abort
from geoip import geolite2
import datetime
from sqlalchemy.engine import ResultProxy, RowProxy
import decimal
import json
import random
from flask import current_app, has_request_context


def dev_env():
    if current_app.config['DEBUG']:
        return True
    else:
        return False


def _get_current_context():
    if has_request_context():
        return request

    if current_app:
        return current_app


class JSONEncoder(json.JSONEncoder):
    """JSONEncoder subclass that knows how to encode date/time and
    decimal types, and also ResultProxy/RowProxy of SQLAlchemy.
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, ResultProxy):
            return list(o)
        elif isinstance(o, RowProxy):
            return dict(o)


def json_dumps(data):
    return json.dumps(data, cls=JSONEncoder)


def paginate(query_set, page, page_size, serializer):
    count = query_set.count()

    if page < 1:
        abort(400, message='Page must be positive integer.')

    if (page - 1) * page_size + 1 > count > 0:
        abort(400, message='Page is out of range.')

    if page_size > 250 or page_size < 1:
        abort(400, message='Page size is out of range (1-250).')

    results = query_set.paginate(page, page_size)

    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': [serializer(result) for result in results.items],
    }


def generate_token(length):
    chars = ('abcdefghijklmnopqrstuvwxyz'
             'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '0123456789')

    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))


def get_location(ip):
    if ip is None:
        return "Unknown"

    match = geolite2.lookup(ip)
    if match is None:
        return "Unknown"

    return match.country


def user_agent():
    browser = request.user_agent.browser
    platform = request.user_agent.platform
    uas = request.user_agent.string
    browser_tuples = ('safari', 'chrome', 'firefox')
    if browser in browser_tuples:
        client = 'web'
    else:
        client = uas
    if platform == 'iphone':
        if browser not in browser_tuples:
            client = 'iphone'
    elif platform == 'android':
        if browser not in browser_tuples:
            client = 'AN'
    elif re.search('iPad', uas):
        if browser not in browser_tuples:
            client = 'iPad'
    elif re.search('Windows Phone OS', uas):
        client = 'WinPhone'
    elif re.search('BlackBerry', uas):
        client = 'BlackBerry'
    return client



