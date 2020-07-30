"""
# @Time    : 2020/7/30 11:30
# @Author  : tmackan
"""
import sys
import time


def retry(func):
    def _(*args, **kwargs):
        tries = 3
        while tries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(sys.stderr, 'error while %s' %func.func_name, tries, e, args, kwargs)
                tries -= 1
                if tries == 0:
                    raise
                time.sleep(0.1)
    return _
