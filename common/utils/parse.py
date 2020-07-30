"""
# @Time    : 2020/7/30 16:36
# @Author  : tmackan
"""
import re
from urllib.parse import quote_plus, unquote_plus


_ASCII_re = re.compile(r'\A[\x00-\x7f]*\Z')


def is_ascii_str(text):
    return isinstance(text, str) and _ASCII_re.match(text)


def url_escape(string):
    # convert into a list of octets
    string = string.encode("utf8")
    return quote_plus(string)


def url_unescape(string):
    text = unquote_plus(string)
    if not is_ascii_str(text):
        text = text.decode("utf8")
    return text


def trim(string):
    return string.strip()
