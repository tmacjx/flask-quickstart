"""
# @Author  wk
# @Time 2020/4/23 10:39

"""
from datetime import datetime, date
import time
import numbers

DATE_FORMAT_DEFAULT = "%Y-%m-%d"
DATETIME_FORMAT_DEFAULT = "%Y-%m-%d %H:%M:%S"


def format_date(dt, formatter=DATE_FORMAT_DEFAULT):
    """
    :param dt:
    :param formatter:
    :return:
    """
    if isinstance(dt, datetime):
        return datetime.strftime(dt, formatter)
    elif isinstance(dt, date):
        return date.strftime(dt, formatter)
    else:
        return None


def format_datetime(dt, formatter=DATETIME_FORMAT_DEFAULT):
    """
    :param dt:
    :param formatter:
    :return:
    """
    if isinstance(dt, numbers.Real):
        dt = datetime.fromtimestamp(float(dt))
    if isinstance(dt, datetime):
        return datetime.strftime(dt, formatter)
    else:
        return None


def to_timestamp(dt=None, formatter=DATETIME_FORMAT_DEFAULT):
    """
    datetime转为timestamp
    :param dt:
    :param formatter
    :return:
    """
    if dt:
        if isinstance(dt, str):
            dt = datetime.strptime(dt, formatter)
    else:
        dt = datetime.now()
    stamp = time.mktime(dt.timetuple())
    return str(int(stamp) * 1000)


def to_datetime(o, formatter=DATETIME_FORMAT_DEFAULT):
    if isinstance(o, str):
        dt = datetime.strptime(o, formatter)
        return dt
    else:
        return None


def to_date(o, formatter=DATE_FORMAT_DEFAULT):
    if isinstance(o, str):
        dt = datetime.strptime(o, formatter).date()
        return dt
    else:
        return None


# if __name__ == "__main__":
#     # res = format_date(datetime.now())
#     # print(res)
#     # res = format_date(datetime.now().date())
#     # print(res)
#     # res = format_datetime(datetime.now())
#     # print(res)
#     # res = format_datetime(1587623323.000)
#     # print(res)
#     # res = to_timestamp(datetime.now())
#     # print(res)
#     # res = to_timestamp()
#     # print(res)
#     # res = to_datetime("2020-02-02 11:11:11")
#     # print(res)
#     # res = to_date("2020-02-02")
#     # print(res)
#     res = to_timestamp("2020-02-02 11:11:11")
#     print(res)

