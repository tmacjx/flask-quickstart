"""
# @Time    : 2020/12/14 22:59
# @Author  : tmackan
"""

from __future__ import absolute_import

import logging
import six
from uuid import uuid4

from contextlib import contextmanager


logger = logging.getLogger(__name__)


class UnableToAcquireLock(Exception):
    """Exception raised when a lock cannot be acquired."""


class Lock(object):
    def __init__(self, backend):
        self.backend = backend

    def acquire_safe(self, key, duration):
        """
        Attempt to acquire the lock.

        If the lock is successfully acquired, this method returns a context
        manager that will automatically release the lock when exited. If the
        lock cannot be acquired, an ``UnableToAcquireLock`` error will be
        raised.

        获取锁后, 立马删除
        with acquire_safe(key, duration) as res:
            if res == 1:
               print("获取成功")
            else:
               print("获取失败")

        :param key:
        :param duration:
        :return:
        """
        res = self.acquire(key, duration)

        @contextmanager
        def release():
            try:
                yield res
            finally:
                self.release(key)

        return release()

    def acquire(self, key, duration):
        """
        """
        try:
            res = self.backend.acquire(key, duration)
        except Exception as error:
            res = -1
            six.raise_from(
                UnableToAcquireLock(u"Unable to acquire {!r} due to error: {}".format(self, error)),
                error,
            )
        return res

    def release(self, key):
        """
        Attempt to release the lock.

        Any exceptions raised when attempting to release the lock are logged
        and suppressed.
        """
        try:
            self.backend.release(key)
        except Exception as error:
            logger.warning("Failed to release %r due to error: %r", self, error, exc_info=True)

    def locked(self, key):
        """
        See if the lock has been taken somewhere else.
        """
        return self.backend.locked(key)


class LockBackend(object):
    """
    Interface for providing lock behavior that is used by the
    ``sentry.utils.locking.Lock`` class.
    """

    def acquire(self, key, duration):
        """
        Acquire a lock, represented by the given key for the given duration (in
        seconds.) This method should attempt to acquire the lock once, in a
        non-blocking fashion, allowing attempt retry policies to be defined
        separately. A routing key may also be provided to control placement,
        but how or if it is implemented is dependent on the specific backend
        implementation.

        The return value is not used. If the lock cannot be acquired, an
        exception should be raised.
        """
        raise NotImplementedError

    def release(self, key):
        """
        Release a lock. The return value is not used.
        """
        raise NotImplementedError

    def locked(self, key):
        """
        Check if a lock has been taken.
        """
        raise NotImplementedError


class RedisLockBackend(LockBackend):

    delete_lock_script = """
        local key = KEYS[1]
        local uuid = ARGV[1]
    
        local value = redis.call('GET', key)
        if not value then
            return redis.error_reply(string.format("No lock at key exists at key: %s", key))
        elseif value ~= uuid then
            return redis.error_reply(string.format("Lock at %s was set by %s, and cannot be released by %s.", key, 
            value, uuid))
        else
            redis.call('DEL', key)
            return redis.status_reply("OK")
        end
    """

    def __init__(self, client, prefix="l:", uuid=None):
        if uuid is None:
            uuid = uuid4().hex

        self.client = client
        self.prefix = prefix
        self.uuid = uuid

    def get_client(self):
        return self.client

    def prefix_key(self, key):
        return u"{}{}".format(self.prefix, key)

    def acquire(self, key, duration):
        full_key = self.prefix_key(key)
        if self.client.set(full_key, self.uuid, ex=duration, nx=True) is not True:
            raise Exception(u"Could not set key: {!r}".format(full_key))

    def release(self, key, routing_key=None):
        self.client.register_script(RedisLockBackend.delete_lock_script)(keys=(self.prefix_key(key),),
                                                                         args=(self.uuid,))

    def locked(self, key, routing_key=None):
        return self.client.get(self.prefix_key(key)) is not None


class LockManager(object):
    def __init__(self, backend):
        self.backend = backend

    def __getattr__(self, name):
        return getattr(self.backend, name)

