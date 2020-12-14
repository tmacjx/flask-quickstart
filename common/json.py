"""
# @Time    : 2020/12/14 22:11
# @Author  : tmackan
"""
import datetime
from uuid import UUID
from simplejson import JSONEncoder, JSONEncoderForHTML, _default_decoder


def extended_encoder(x):
    if isinstance(x, datetime.date):
        return datetime.date.strftime(x, "%Y-%m-%d")
    if isinstance(x, datetime.datetime):
        return datetime.datetime.strftime(x, "%Y-%m-%d %H:%M:%S")
    if isinstance(x, UUID):
        return str(x)


_default_encoder = JSONEncoder(
    separators=(",", ":"),
    ignore_nan=True,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    indent=None,
    encoding="utf-8",
    default=extended_encoder,
)


_default_escaped_encoder = JSONEncoderForHTML(
    separators=(",", ":"),
    ignore_nan=True,
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    indent=None,
    encoding="utf-8",
    default=extended_encoder,
)


def dump(value, fp):
    for chunk in _default_encoder.iterencode(value):
        fp.write(chunk)


def dumps(value, escape=False):
    if escape:
        return _default_escaped_encoder.encode(value)
    return _default_encoder.encode(value)


def load(fp):
    return loads(fp.read())


def loads(value):
    return _default_decoder.decode(value)
