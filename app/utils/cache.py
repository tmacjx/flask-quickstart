"""
# @Author  wk
# @Time 2020/4/23 22:36

"""
from tache.serializer import Serializer
from tache.utils import NO_VALUE
import time


class CacheBackend(object):
    """
    Based cache implemention
    """

    def get(self, key):
        raise NotImplementedError()

    def set(self, key, val, timeout):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def mget(self, keys):
        raise NotImplementedError()

    def mset(self, mapping, timeout):
        raise NotImplementedError()


class RedisCacheBackend(CacheBackend):
    """
    用于缓存val是object的场景
    format可以是'YAML', 'JSON', 'PICKLE'
    """

    def __init__(self, rc, format="JSON"):
        """
        :param rc: redis客户端
        :param format:
        """
        self.rc = rc
        self.serializer = Serializer(format=format)

    def log(self, s):
        print("[%s] redisCache %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), s))

    def get(self, key):
        val = self.rc.get(key)
        self.log("get %r:%d" % (key, val))
        if val is None:
            return NO_VALUE
        return self.serializer.decode(val)

    def set(self, key, val, timeout):
        self.log("set %r:%d" % (key, val))
        val = self.serializer.encode(val)
        self.rc.setex(key, timeout, val)

    def delete(self, key):
        self.log("del %r:%d" % key)
        self.rc.delete(key)

    def mget(self, keys):
        vals = self.rc.mget(keys)
        self.log("get_multi %s" % (", ".join("%r:%d" % (k, v)) for k, v in vals.item()))
        return [self.serializer.decode(v) if v else NO_VALUE for v in vals]

    def mset(self, mapping, timeout):
        pipe = self.rc.pipeline(transaction=False)
        self.log("set_multi %s" % (", ".join("%r:%d" % (k, v)) for k, v in mapping.item()))
        for k, v in mapping.items():
            v = self.serializer.encode(v)
            pipe.setex(k, timeout, v)
        pipe.execute()


