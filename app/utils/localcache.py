"""
# @Author  wk
# @Time 2020/4/24 17:11

"""
import sys
import functools
import threading
from collections import UserDict, OrderedDict
from functools import wraps
import kombu

KEYWORD_MARK = object()


def simple_memoize(obj):
    """
    Local cache of the function return value
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


class CacheProperty(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.

    Optional ``name`` argument allows you to make cached properties of other
    methods. (e.g.  url = cached_property(get_absolute_url, name='url') )
    """
    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.name] = self.func(instance)
        return res


class LRUCache(UserDict):
    """LRU Cache implementation using a doubly linked list to track access.

    Arguments:
        limit (int): The maximum number of keys to keep in the cache.
            When a new key is inserted and the limit has been exceeded,
            the *Least Recently Used* key will be discarded from the
            cache.
    """

    def __init__(self, limit=None, *args, **kwargs):
        self.limit = limit
        self.mutex = threading.RLock()
        self.data = OrderedDict()
        super(LRUCache, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        with self.mutex:
            value = self[key] = self.data.pop(key)
            return value

    def update(self, *args, **kwargs):
        with self.mutex:
            data, limit = self.data, self.limit
            data.update(*args, **kwargs)
            if limit and len(data) > limit:
                # pop additional items in case limit exceeded
                for _ in range(len(data) - limit):
                    data.popitem(last=False)

    def popitem(self, last=True):
        with self.mutex:
            return self.data.popitem(last)

    def __setitem__(self, key, value):
        # remove least recently used key.
        with self.mutex:
            if self.limit and len(self.data) >= self.limit:
                self.data.pop(next(iter(self.data)))
            self.data[key] = value

    def __iter__(self):
        return iter(self.data)

    def _iterate_items(self):
        with self.mutex:
            for k in self:
                try:
                    yield (k, self.data[k])
                except KeyError:  # pragma: no cover
                    pass
    iteritems = _iterate_items

    def _iterate_values(self):
        with self.mutex:
            for k in self:
                try:
                    yield self.data[k]
                except KeyError:  # pragma: no cover
                    pass

    itervalues = _iterate_values

    def _iterate_keys(self):
        # userdict.keys in py3k calls __getitem__
        with self.mutex:
            return self.data.keys()
    iterkeys = _iterate_keys

    def incr(self, key, delta=1):
        with self.mutex:
            # this acts as memcached does- store as a string, but return a
            # integer as long as it exists and we can cast it
            newval = int(self.data.pop(key)) + delta
            self[key] = str(newval)
            return newval

    def __getstate__(self):
        d = dict(vars(self))
        d.pop('mutex')
        return d

    def __setstate__(self, state):
        self.__dict__ = state
        self.mutex = threading.RLock()

    if sys.version_info[0] == 3:  # pragma: no cover
        keys = _iterate_keys
        values = _iterate_values
        items = _iterate_items
    else:  # noqa

        def keys(self):
            return list(self._iterate_keys())

        def values(self):
            return list(self._iterate_values())

        def items(self):
            return list(self._iterate_items())


def memoize(maxsize=None, keyfun=None, Cache=LRUCache):
    """Decorator to cache function return value."""
    def _memoize(fun):
        mutex = threading.Lock()
        cache = Cache(limit=maxsize)

        @wraps(fun)
        def _M(*args, **kwargs):
            if keyfun:
                key = keyfun(args, kwargs)
            else:
                key = args + (KEYWORD_MARK,) + tuple(sorted(kwargs.items()))
            try:
                with mutex:
                    value = cache[key]
            except KeyError:
                value = fun(*args, **kwargs)
                _M.misses += 1
                with mutex:
                    cache[key] = value
            else:
                _M.hits += 1
            return value

        def clear():
            """Clear the cache and reset cache statistics."""
            cache.clear()
            _M.hits = _M.misses = 0

        _M.hits = _M.misses = 0
        _M.clear = clear
        _M.original_func = fun
        return _M

    return _memoize


class lazy(object):
    """Holds lazy evaluation.

    Evaluated when called or if the :meth:`evaluate` method is called.
    The function is re-evaluated on every call.

    Overloaded operations that will evaluate the promise:
        :meth:`__str__`, :meth:`__repr__`, :meth:`__cmp__`.
    """

    def __init__(self, fun, *args, **kwargs):
        self._fun = fun
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        return self.evaluate()

    def evaluate(self):
        return self._fun(*self._args, **self._kwargs)

    def __str__(self):
        return str(self())

    def __repr__(self):
        return repr(self())

    def __eq__(self, rhs):
        return self() == rhs

    def __ne__(self, rhs):
        return self() != rhs

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    def __reduce__(self):
        return (self.__class__, (self._fun,), {'_args': self._args,
                                               '_kwargs': self._kwargs})


class LocalCache(object):
    def __init__(self, maxsize=None):
        self.dataset = LRUCache(maxsize)

    def set(self, key, val):
        _, version = self.dataset.get(key, (None, -1))
        self.dataset[key] = (val, version + 1)
        return True

    def add(self, key, val):
        if key not in self.dataset.keys():
            self.dataset[key] = (val, 1)
            return True
        else:
            return False

    def set_multi(self, values, return_failure=False):
        for k, v in values.iteritems():
            _, version = self.dataset.get(k, (None, -1))
            self.dataset[k] = (v, version + 1)
        if return_failure:
            return True, []
        else: return True

    def cas(self, key, val, cas=0):
        if key in self.dataset:
            _, version = self.dataset.get(key)
            if version == cas:
                self.dataset[key] = (val, version + 1)
                return True
        return False

    def delete(self, key):
        if key in self.dataset:
            del self.dataset[key]
        return 1

    def delete_multi(self, keys, return_failure=False):
        for k in keys:
            self.delete(k)
        if return_failure:
            return True, []
        else:
            return True

    def get(self, key):
        return self.dataset.get(key, (None, 0))[0]

    def gets(self, key):
        return self.dataset.get(key, (None, 0))

    def get_raw(self, key):
        raise NotImplementedError()

    def get_multi(self, keys):
        rets = {}
        for k in keys:
            r = self.dataset.get(k)
            if r is not None:
                rets[k] = r[0]
        return rets

    def get_list(self, keys):
        return [self.dataset.get(k)[0] for k in keys]

    def incr(self, key, val=1):
        raise NotImplementedError()

    def decr(self, key, val=1):
        raise NotImplementedError()

    def clear(self):
        self.dataset.clear()
