"""
# @Author  wk
# @Time 2019/10/11 11:13

"""
import base64
import binascii
import socket
import re
import os
import time
import uuid
from datetime import datetime
import fcntl
import logging
from flask import request
from flask import g
import threading
from collections import OrderedDict
import traceback

from logging.handlers import TimedRotatingFileHandler


class MultiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):
    _stream_lock = None

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        # dfn = self.baseFilename + '.' + time.strftime(self.suffix, timeTuple)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        # 加锁保证rename的进程安全
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            fcntl.lockf(self.stream_lock, fcntl.LOCK_EX)
            try:
                if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
                    os.rename(self.baseFilename, dfn)
            finally:
                fcntl.lockf(self.stream_lock, fcntl.LOCK_UN)
        # 加锁保证删除文件的进程安全
        if self.backupCount > 0:
            if self.getFilesToDelete():
                fcntl.lockf(self.stream_lock, fcntl.LOCK_EX)
                try:
                    files_to_delete = self.getFilesToDelete()
                    if files_to_delete:
                        for s in files_to_delete:
                            os.remove(s)
                finally:
                    fcntl.lockf(self.stream_lock, fcntl.LOCK_UN)
        if not self.delay:
            # _open默认是以‘a'的方式打开，是进程安全的
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

    @property
    def stream_lock(self):
        if not self._stream_lock:
            self._stream_lock = self._openLockFile()
        return self._stream_lock

    def _getLockFile(self):
        # Use 'file.lock' and not 'file.log.lock' (Only handles the normal "*.log" case.)
        if self.baseFilename.endswith('.log'):
            lock_file = self.baseFilename[:-4]
        else:
            lock_file = self.baseFilename
        lock_file += '.lock'
        return lock_file

    def _openLockFile(self):
        lock_file = self._getLockFile()
        return open(lock_file, 'w')


class ExecutedOutsideContext(Exception):
    """
    Exception to be raised if a fetcher was called outside its context
    """
    pass


class MultiContextRequestIdFetcher(object):
    """
    A callable that can fetch request id from different context as Flask, Celery etc.
    """

    def __init__(self):
        """
        Initialize
        """
        self.ctx_fetchers = []

    def __call__(self):

        for ctx_fetcher in self.ctx_fetchers:
            try:
                return ctx_fetcher()
            except ExecutedOutsideContext:
                continue
        return None

    def register_fetcher(self, ctx_fetcher):
        """
        Register another context-specialized fetcher
        :param Callable ctx_fetcher: A callable that will return the id or raise ExecutedOutsideContext if it was
         executed outside its context
        """
        if ctx_fetcher not in self.ctx_fetchers:
            self.ctx_fetchers.append(ctx_fetcher)


NO_REQUEST_ID = "none"


def dj_ctx_get_request_id():
    local = threading.local()
    req_id = getattr(local, 'request_id', NO_REQUEST_ID)
    return req_id


def flask_ctx_get_request_id():
    """
    Get request id from flask's G object
    :return: The id or None if not found.
    """
    from flask import _app_ctx_stack as stack  # We do not support < Flask 0.9

    if stack.top is None:
        raise ExecutedOutsideContext()

    g_object_attr = "traceId"
    return g.get(g_object_attr, None)


current_request_id = MultiContextRequestIdFetcher()
current_request_id.register_fetcher(flask_ctx_get_request_id)


# DEFAULT_FORMAT = logging.Formatter("%(asctime)s - %(reqId)s - [%(levelname)s]  - %(filename)s - %(lineno)d - "
#                                    "[%(process)d:%(thread)d] - %(reqUri)s - [%(other)s]:  %(message)s")
DEFAULT_FORMAT = logging.Formatter("%(asctime)s - %(reqId)s - [%(levelname)s]  - %(filename)s - %(lineno)d - "
                                   "[%(process)d:%(thread)d] - %(message)s")


class RequestIDLogFilter(logging.Filter):
    """
    Log filter to inject the current request id of the request under `log_record.request_id`
    """

    def filter(self, log_record):
        log_record.reqId = current_request_id()
        return log_record


CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,

    root={"level": "INFO", "handlers": ["console"]},
    loggers={
        "app.error": {
            "level": "INFO",
            "handlers": ["service_console"],
            "propagate": True,
            "qualname": "app.service"
        },

        "app.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": True,
            "qualname": "app.access"
        }
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout"
        },
        "service_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr"
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        }
    }
)


# todo 改变格式
# todo access单独一个日志文件，service单独一个日志文件
class HTTPInfo(object):
    def __init__(self, request_obj, resp_obj):
        super(HTTPInfo, self).__init__()
        self._request = request_obj
        self._response = resp_obj

    def get_req_uri(self):
        raise NotImplemented

    def get_http_method(self):
        raise NotImplemented

    @staticmethod
    def get_server_ip():
        return socket.gethostname()

    def get_client_ip(self):
        raise NotImplemented

    def get_sdk_version(self):
        raise NotImplemented

    @staticmethod
    def is_json_type(content_type):
        return content_type == 'application/json'

    def get_req_data(self):
        raise NotImplemented

    def get_agent_type(self):
        raise NotImplemented

    def get_status_code(self):
        return self._response.status_code

    def get_resp_size(self):
        return self._response.calculate_content_length()

    def get_resp_content_type(self):
        return self._response.content_type


class FlaskHttpInfo(HTTPInfo):

    def __init__(self, request_obj, resp_obj):
        super(FlaskHttpInfo, self).__init__(request_obj, resp_obj)

    def get_req_uri(self):
        return self._request.full_path

    def get_http_method(self):
        return self._request.method

    def get_client_ip(self):
        real_ip = self._request.headers.get('X-Real-Ip', request.remote_addr)
        return real_ip

    def get_sdk_version(self):
        return self._request.headers.get('SDKVersion')

    def get_req_data(self):
        if self.is_json_type(request.mimetype):
            data = self._request.data
        else:
            data = self._request.json
        return data

    def get_agent_type(self):
        """
        获取请求来源
        """
        browser = self._request.user_agent.browser
        platform = self._request.user_agent.platform
        uas = self._request.user_agent.string
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

    @staticmethod
    def get_client_version():
        return request.headers.get('SDKVersion')

    def get_userid(self):
        """
        获取账号ID
        :return:
        """
        userid = self._request.args.get('userid')
        return userid

    def get_login_token(self):
        """
        获取登录token
        :return:
        """
        token = self._request.headers.get('token') or self._request.args.get('sessionid')
        return token

    def get_info(self):
        data = OrderedDict()
        # data['request_start'] = datetime.utcnow()
        data['serverIp'] = self.get_server_ip()
        data['clientIp'] = self.get_client_ip()
        data['logSource'] = self.get_agent_type()
        data['reqMethod'] = self.get_http_method()
        data['reqData'] = self.get_req_data()
        data['reqUri'] = self.get_req_uri()
        data['device'] = self.get_agent_type()
        data['sdkVersion'] = self.get_sdk_version()
        data['userId'] = self.get_userid()
        data['token'] = self.get_login_token()
        data['respStat'] = self.get_status_code()
        data['respSizeB'] = self.get_resp_size()
        data['respContentType'] = self.get_resp_content_type()
        return data


class SafeAtoms(dict):

    def __init__(self, atoms):
        dict.__init__(self)
        for key, value in atoms.items():
            if isinstance(value, str):
                self[key] = value.replace('"', '\\"')
            else:
                self[key] = value

    def __getitem__(self, k):
        if k.startswith("{"):
            kl = k.lower()
            if kl in self:
                return super().__getitem__(kl)
            else:
                return "-"
        if k in self:
            return super().__getitem__(k)
        else:
            return '-'


# todo 按时间大小切割


class FlaskLogStash(object):

    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }
    loglevel = logging.INFO

    service_fmt = logging.Formatter("%(asctime)s - %(reqId)s - [%(levelname)s]  - %(filename)s - %(lineno)d - "
                                    "[%(process)d:%(thread)d] - %(message)s")

    datefmt = r"[%Y-%m-%d %H:%M:%S %z]"

    access_log_fmt = "%(message)s"

    atoms_wrapper_class = SafeAtoms

    def __init__(self, log_format=DEFAULT_FORMAT, level='DEBUG', app=None):

        # self.log_format = log_format
        # self.level = level
        # self._logger = logging.getLogger('api-logger')
        # self._logger.setLevel(logging.DEBUG)
        # self._logger.propagate = 0

        self.service_log = logging.getLogger("app.service")
        self.service_log.propagate = False
        self.access_log = logging.getLogger("app.access")
        self.access_log.propagate = False
        self.error_handlers = []
        self.access_handlers = []

        if app:
            self.app = app
            self.init_app(app)

    def setup(self, cfg):
        pass

    def critical(self, msg, *args, **kwargs):
        self.service_log.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.service_log.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.service_log.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.service_log.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.service_log.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.service_log.exception(msg, *args, **kwargs)

    def log(self, lvl, msg, *args, **kwargs):
        if isinstance(lvl, str):
            lvl = self.LOG_LEVELS.get(lvl.lower(), logging.INFO)
        self.service_log.log(lvl, msg, *args, **kwargs)

    def _get_user(self, headers):
        user = None
        http_auth = headers.get("HTTP_AUTHORIZATION")
        if http_auth and http_auth.lower().startswith('basic'):
            auth = http_auth.split(" ", 1)
            if len(auth) == 2:
                try:
                    # b64decode doesn't accept unicode in Python < 3.3
                    # so we need to convert it to a byte string
                    auth = base64.b64decode(auth[1].strip().encode('utf-8'))
                    # b64decode returns a byte string
                    auth = auth.decode('utf-8')
                    auth = auth.split(":", 1)
                except (TypeError, binascii.Error, UnicodeDecodeError) as exc:
                    self.debug("Couldn't get username: %s", exc)
                    return user
                if len(auth) == 2:
                    user = auth[0]
        return user

    def now(self):
        """ return date in Apache Common Log Format """
        return time.strftime('[%d/%b/%Y:%H:%M:%S %z]')

    def atoms(self, resp, req, environ, request_time):
        """ Gets atoms for log formating.
        """
        status = resp.status
        if isinstance(status, str):
            status = status.split(None, 1)[0]

        atoms = {
            'h': environ.get('REMOTE_ADDR', '-'),
            'l': '-',
            'u': self._get_user(environ) or '-',
            't': self.now(),
            'reqId': self.last_req_id,
            'r': "%s %s %s" % (environ['REQUEST_METHOD'],
                               environ['RAW_URI'],
                               environ["SERVER_PROTOCOL"]),
            's': status,
            'm': environ.get('REQUEST_METHOD'),
            'U': environ.get('PATH_INFO'),
            'q': environ.get('QUERY_STRING'),
            'H': environ.get('SERVER_PROTOCOL'),
            'b': getattr(resp, 'sent', None) is not None and str(resp.sent) or '-',
            'B': getattr(resp, 'sent', None),
            'f': environ.get('HTTP_REFERER', '-'),
            'a': environ.get('HTTP_USER_AGENT', '-'),
            'T': request_time.seconds,
            'D': (request_time.seconds * 1000000) + request_time.microseconds,
            'M': (request_time.seconds * 1000) + int(request_time.microseconds/1000),
            'L': "%d.%06d" % (request_time.seconds, request_time.microseconds),
            'p': "<%s>" % os.getpid(),
        }

        # add request headers
        if hasattr(req, 'headers'):
            req_headers = req.headers
        else:
            req_headers = req

        if hasattr(req_headers, "items"):
            req_headers = req_headers.items()

        atoms.update({"{%s}i" % k.lower(): v for k, v in req_headers})

        resp_headers = resp.headers
        if hasattr(resp_headers, "items"):
            resp_headers = resp_headers.items()

        # add response headers
        atoms.update({"{%s}o" % k.lower(): v for k, v in resp_headers})

        # add environ variables
        environ_variables = environ.items()
        atoms.update({"{%s}e" % k.lower(): v for k, v in environ_variables})

        return atoms

    def access(self, resp, req, environ, request_time):
        """ See http://httpd.apache.org/docs/2.0/logs.html#combined
        for format details
        """
        # wrap atoms:
        # - make sure atoms will be test case insensitively
        # - if atom doesn't exist replace it by '-'
        safe_atoms = self.atoms_wrapper_class(self.atoms(resp, req, environ,
            request_time))
        try:
            self.access_log.info(self.access_log_fmt, safe_atoms)
        except:
            self.error(traceback.format_exc())


    @property
    def last_req_id(self):
        try:
            return g.last_req_id
        except Exception:
            pass
        return getattr(self, '_last_req_id', None)

    @last_req_id.setter
    def last_req_id(self, value):
        """
        reqID
        :param value:
        :return:
        """
        self._last_req_id = value
        try:
            g.last_req_id = value
        except Exception:
            pass

    @property
    def last_request_start(self):
        """
        request开始的时间
        :return:
        """
        try:
            return g.last_request_start
        except Exception:
            pass
        return getattr(self, '_last_request_start', None)

    @last_request_start.setter
    def last_request_start(self, value):
        self._last_request_start = value
        try:
            g.last_request_start = value
        except Exception:
            pass

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, val):
        self._logger = val

    def init_app(self, app):
        log_path = app.config.get('LOG_PATH', 'app.log')
        log_level = app.config.get("LOG_LEVEL", "DEBUG")

        def __init_logger(logger, path, level, formatter):

            log_filter = RequestIDLogFilter()

            # todo 增加大小切割
            fh = MultiProcessTimedRotatingFileHandler(path, when='MIDNIGHT', interval=1)
            fh.setLevel(level)
            # 定义handler的输出格式
            fh.setFormatter(formatter)
            fh.addFilter(log_filter)
            # 给logger添加handler
            logger.addHandler(fh)

            if level == 'DEBUG':
                # 再创建一个handler，用于输出到控制台
                ch = logging.StreamHandler()
                ch.setLevel(level)
                ch.setFormatter(formatter)
                ch.addFilter(log_filter)
                logger.addHandler(ch)

        __init_logger(self.service_log, log_path, log_level, self.service_fmt)

        @app.before_request
        def before_request():
            self.last_req_id = str(uuid.uuid1().hex)
            self.last_request_start = datetime.utcnow()

        @app.after_request
        def after_request(response):
            if self.last_req_id:
                response.headers['X-req-ID'] = self.last_req_id
            http_info = FlaskHttpInfo(request, response).get_info()
            req_url = http_info.pop('reqUri', '')
            time_delta = datetime.utcnow() - self.last_request_start
            http_info['respTimeMs'] = int(time_delta.total_seconds()) * 1000 + int(time_delta.microseconds / 1000)
            log_http_str = "&".join("%s=%s" % (k, v) for k, v in http_info.items())
            extra_msg = "%s %s %s" % (req_url, log_http_str, 'Request')
            self.logger.info(extra_msg)
            return response


