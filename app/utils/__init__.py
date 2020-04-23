"""
# @Author  wk
# @Time 2020/4/22 10:35

"""
from .elklog import *
from flask import request, abort
from geoip import geolite2
from sqlalchemy.orm.query import Query
import decimal
import json
import random
from flask import current_app, has_request_context


def _get_current_context():
    if has_request_context():
        return request

    if current_app:
        return current_app


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoding class, to handle Decimal and datetime.date instances."""

    def default(self, o):
        # Some SQLAlchemy collections are lazy.
        if isinstance(o, Query):
            return list(o)
        if isinstance(o, decimal.Decimal):
            return float(o)

        if isinstance(o, (datetime.date, datetime.time)):
            return o.isoformat()

        if isinstance(o, datetime.timedelta):
            return str(o)

        super(JSONEncoder, self).default(o)


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



