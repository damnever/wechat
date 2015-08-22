# -*- coding: utf-8 -*-

from __future__ import print_function, division

import threading

import redis


class Connection(object):

    _thread_lock = threading.Lock()
    _con = None

    @classmethod
    def setup(cls, **kwargs):
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 6379)
        db = kwargs.get('db', 0)
        password = kwargs.get('password', '')
        cls._config_connection(host, port, db, password)
        cls._conn = redis.StrictRedis(**kwargs)

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            with cls._thread_lock:
                cls._instance = cls._make_instance()
        return cls._instance

    @classmethod
    def use_connection(cls, url):
        cls._conn = redis.from_url(url)

    @classmethod
    def _make_instance(cls):
        return cls._conn

    @staticmethod
    def _config_connection(host, port, db, password):
        password = ':' + password if password else ''
        url = 'redis://{0}@{1}:{2}/{3}'.format(password, host, port, db)
        with open('connection.config', 'w') as f:
            f.write(url)
