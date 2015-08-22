# -*- coding: utf-8 -*-

from __future__ import print_function

import time

import tqueue
import connection


def exc(*args, **kwargs):
    raise TypeError('{0}, {1}'.format(args, kwargs))

def foobar(*args, **kwargs):
    return args, kwargs

class A(object):
    def foobar(self, *args, **kwargs):
        return args, kwargs

class B(object):
    def __call__(self, *args, **kwargs):
        return args, kwargs


if __name__ == '__main__':
    connection.Connection.setup(db=3)

    q = tqueue.Queue()
    id1 = q.enqueue(exc, args=('foo',), kwargs={'e': 'bar'})
    id2 = q.enqueue(foobar, ('foobar',), {'foo': 'bar'})
    id3 = q.enqueue(A().foobar, ('foobar',), {'foo': 'bar'})
    id4 = q.enqueue(B(), ('foobar',), {'foo': 'bar'})
    id5 = q.enqueue(pow, (4, 2),)

    ids = [id1, id2, id3, id4, id5]
    results = dict()

    while True:
        for id_ in ids:
            result = tqueue.get_result_by_id(id_)
            if result is not None:
                results[id_] = result
            else:
                if tqueue.is_waiting(id_):
                    print('#{0} is waiting...'.format(id_))
                elif tqueue.is_failed(id_):
                    print('#{0} need retry...'.format(id_))

        if len(results) == len(ids):
            break
        else:
            time.sleep(0.2)

    print('-'*10)
    for k, v in results.items():
        print('#{0} : {1}'.format(k, v))

    time.sleep(10)
    tqueue.clear_all()
