# -*- coding: utf-8 -*-

"""
Queue base on Redis. FIFO.
"""

from __future__ import print_function, division

from task import Task
from connection import Connection
from utils import dumps, loads, ClassUnpickler, NoSuchIdExists


def get_result_by_id(task_id):
    if is_done(task_id):
        return SuccessQueue().get_task_result(task_id)
    elif is_dead(task_id):
        return DeadQueue().get_task_exc_info(task_id)
    return None

def is_waiting(task_id):
    return task_id in Queue()

def is_done(task_id):
    return task_id in SuccessQueue()

def is_failed(task_id):
    return task_id in FailQueue()

def is_dead(task_id):
    return task_id in DeadQueue()

def clear_all():
    Queue().clear()
    SuccessQueue().clear()
    FailQueue().clear()
    DeadQueue().clear()


class _BaseQueue(object):

    def __init__(self, conn=None):
        if conn is None:
            conn = Connection.instance()
        self._conn = conn

    def size(self):
        return self._conn.llen(self.queue_key())

    def is_empty(self):
        return self.size() == 0

    def clear(self):
        if self.is_empty():
            return
        item_keys = [self.queue_item_key(id_) for id_ in self.all_task_ids]
        self._conn.delete(*item_keys)
        self._conn.delete(self.queue_key())

    def __contains__(self, task_id):
        return (task_id in self.all_task_ids)

    @property
    def all_task_ids(self):
        return iter(self._conn.lrange(self.queue_key(), 0, -1))

    def queue_item_key(self, task_id):
        raise NotImplemented()

    def queue_key(self):
        raise NotImplemented()


class Queue(_BaseQueue):
    """The Queue stores Tasks wait for executing."""

    def __init__(self, *args, **kwargs):
        super(Queue, self).__init__(*args, **kwargs)

    def enqueue(self, callable, args=None, kwargs=None, expire=None):
        task = Task(callable, args, kwargs)
        task_id = task.id
        self._conn.set(self.queue_item_key(task_id), dumps(task), ex=expire)
        self._conn.rpush(self.queue_key(), task_id)
        return task_id

    def dequeue(self):
        if self.is_empty():
            return None
        task_id = self._conn.lpop(self.queue_key())
        item_key = self.queue_item_key(task_id)
        task_raw = self._conn.get(item_key)
        self._conn.delete(item_key)
        task = None
        with ClassUnpickler(task_raw, Task) as unpickler:
            task = unpickler.load()
        return task_id, task_raw, task

    def queue_item_key(self, task_id):
        return 'taskq:{0}:wait'.format(task_id)

    def queue_key(self):
        return 'taskq:all:wait'


class SuccessQueue(_BaseQueue):
    """The Queue stores Tasks.id and task result, if Task
    done without exception.
    """

    def __init__(self, *args, **kwargs):
        super(SuccessQueue, self).__init__(*args, **kwargs)

    def enqueue(self, task_id, result):
        self._conn.rpush(self.queue_key(), task_id)
        self._conn.set(self.queue_item_key(task_id), dumps(result))

    def dequeue(self):
        task_id = self._conn.lpop(self.queue_key())
        item_key = self.queue_item_key(task_id)
        result = self._conn.get(item_key)
        self._conn.delete(item_key)
        return task_id, loads(result)

    def get_task_result(self, task_id):
        """Just return task result by id. Does not remove task id with
        result from queue.
        """
        if task_id not in self:
            raise NoSuchIdExists("{0}".format(task_id))
        result = self._conn.get(self.queue_item_key(task_id))
        return loads(result)

    def get_task_result_nostore(self, task_id):
        """Return task result by id, and remove task id and result
        from queue.
        """
        if task_id not in self:
            raise NoSuchIdExists("{0}".format(task_id))
        new_ids = [id_ for id_ in self.all_task_ids if task_id != id_]
        self._conn.delete(self.queue_key())
        for id_ in new_ids:
            self._conn.rpush(self.queue_key(), id_)
        item_key = self.queue_item_key(task_id)
        result = self._conn.get(item_key)
        self._conn.delete(item_key)
        return loads(result)

    def queue_item_key(self, task_id):
        return 'taskq:{0}:success'.format(task_id)

    def queue_key(self):
        return 'taskq:all:success'


class FailQueue(_BaseQueue):
    """The Queue stores Task objects with exception."""

    def __init__(self, *args, **kwargs):
        super(FailQueue, self).__init__(*args, **kwargs)

    def enqueue(self, task_id, task_raw, exc_info):
        self._conn.rpush(self.queue_key(), task_id)
        self._conn.hmset(self.queue_item_key(task_id),
                         {'task': task_raw, 'exc_info': exc_info})

    def dequeue(self):
        task_id = self._conn.lpop(self.queue_key())
        item_key = self.queue_item_key(task_id)
        task_raw, exc_info = self._conn.hmget(item_key, 'task', 'exc_info')
        self._conn.delete(item_key)
        task = None
        with ClassUnpickler(task_raw, Task) as unpickler:
            task = unpickler.load()
        return task_id, task_raw, task, exc_info

    def queue_item_key(self, task_id):
        return 'taskq:{0}:failed'.format(task_id)

    def queue_key(self):
        return 'taskq:all:failed'


class DeadQueue(_BaseQueue):

    def __init__(self, *args, **kwargs):
        super(DeadQueue, self).__init__(*args, **kwargs)

    def enqueue(self, task_id, exc_info):
        self._conn.rpush(self.queue_key(), task_id)
        self._conn.set(self.queue_item_key(task_id), exc_info)

    def dequeue(self):
        task_id = self._conn.lpop(self.queue_key())
        item_key = self.queue_item_key(task_id)
        exc_info = self._conn.get(item_key)
        self._conn.delete(item_key)
        return exc_info

    def get_task_exc_info(self, task_id):
        if task_id not in self:
            raise NoSuchIdExists("{0}".format(task_id))
        exc_info = self._conn.get(self.queue_item_key(task_id))
        return exc_info

    def queue_item_key(self, task_id):
        return 'taskq:{0}:dead'.format(task_id)

    def queue_key(self):
        return 'taskq:all:dead'
