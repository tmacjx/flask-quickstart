"""
# @Time    : 2020/7/31 11:53
# @Author  : tmackan
"""

from flask import request, abort
from sqlalchemy.orm.query import Query
import decimal
import json
import random
import datetime
import re
from flask import current_app, has_request_context


def make_url_query(args):
    """
    Helper function to return a query url string from a dict
    """
    return '?' + '&'.join('%s=%s' % (key, args[key]) for key in args)


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





def generate_token(length):
    chars = ('abcdefghijklmnopqrstuvwxyz'
             'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '0123456789')

    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))


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



