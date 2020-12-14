from __future__ import absolute_import

import logging
import sys
import threading
import six

from concurrent.futures import Future


logger = logging.getLogger(__name__)


def execute(func, daemon=True):
    future = Future()

    def run():
        if not future.set_running_or_notify_cancel():
            return

        try:
            result = func()
        except Exception as e:
            if six.PY3:
                future.set_exception(e)
            else:
                future.set_exception_info(*sys.exc_info()[1:])
        else:
            future.set_result(result)

    t = threading.Thread(target=run)
    t.daemon = daemon
    t.start()

    return future
