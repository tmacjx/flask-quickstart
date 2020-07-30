"""
# @Author  wk
# @Time 2020/4/24 17:11

"""
import sys
import functools
import threading
from collections import UserDict, OrderedDict
from functools import wraps
# import kombu

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


class memoized_property(object):

    """A read-only @property that is only evaluated once."""

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


class memoized_instancemethod(object):

    """Decorate a method memoize its return value.

    Best applied to no-arg methods: memoization is not sensitive to
    argument values, and will always return the same value even when
    called with different arguments.

    """

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self

        def oneshot(*args, **kw):
            result = self.fget(obj, *args, **kw)
            memo = lambda *a, **kw: result
            memo.__name__ = self.__name__
            memo.__doc__ = self.__doc__
            obj.__dict__[self.__name__] = memo
            return result
        oneshot.__name__ = self.__name__
        oneshot.__doc__ = self.__doc__
        return oneshot


# 无 synchronization 实现 from mako
# class LRUCache(dict):
#
#     """A dictionary-like object that stores a limited number of items,
#     discarding lesser used items periodically.
#
#     this is a rewrite of LRUCache from Myghty to use a periodic timestamp-based
#     paradigm so that synchronization is not really needed.  the size management
#     is inexact.
#     """
#
#     class _Item(object):
#
#         def __init__(self, key, value):
#             self.key = key
#             self.value = value
#             self.timestamp = compat.time_func()
#
#         def __repr__(self):
#             return repr(self.value)
#
#     def __init__(self, capacity, threshold=.5):
#         self.capacity = capacity
#         self.threshold = threshold
#
#     def __getitem__(self, key):
#         item = dict.__getitem__(self, key)
#         item.timestamp = compat.time_func()
#         return item.value
#
#     def values(self):
#         return [i.value for i in dict.values(self)]
#
#     def setdefault(self, key, value):
#         if key in self:
#             return self[key]
#         else:
#             self[key] = value
#             return value
#
#     def __setitem__(self, key, value):
#         item = dict.get(self, key)
#         if item is None:
#             item = self._Item(key, value)
#             dict.__setitem__(self, key, item)
#         else:
#             item.value = value
#         self._manage_size()
#
#     def _manage_size(self):
#         while len(self) > self.capacity + self.capacity * self.threshold:
#             bytime = sorted(dict.values(self),
#                             key=operator.attrgetter('timestamp'), reverse=True)
#             for item in bytime[self.capacity:]:
#                 try:
#                     del self[item.key]
#                 except KeyError:
#                     # if we couldn't find a key, most likely some other thread
#                     # broke in on us. loop around and try again
#                     break

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

