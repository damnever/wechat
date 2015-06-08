#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import threading

import redis


class Rds(object):

    SUBJECT_ONLINE = 'online'
    SUBJECT_OUTLINE = 'outline'
    SUBJECT_NEW_MESSAGE = 'new_message'

    SET_ALL_USERS = 'users:all:online'

    LIST_MESSAGES = 'messages:{from_}:{to}'

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super(Rds, cls).__new__(
                        cls, *args, **kwargs)
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=1):
        self._redis = redis.StrictRedis(host=host, port=port, db=db)
        self._pubsub = self._redis.pubsub()
        self._pubsub.subscribe(self.SUBJECT_ONLINE, self.SUBJECT_OUTLINE,
                               self.SUBJECT_NEW_MESSAGE)

    def subscribe(self, *channels):
        self._pubsub.subscribe(*channels)

    def get_message(self):
        return self._pubsub.get_message()

    def iter_message(self):
        while 1:
            message = self._pubsub.get_message()
            if message:
                yield (message['channel'], message['data'])
            else:
                time.sleep(0.001)

    def publish(self, channel, message):
        self._redis.publish(channel, message)

    def all_online_users(self):
        return list(self._redis.smembers(self.SET_ALL_USERS))

    def online(self, username):
        if not self._redis.sismember(self.SET_ALL_USERS, username):
            self._redis.sadd(self.SET_ALL_USERS, username)
            self._redis.publish(self.SUBJECT_ONLINE, username)

    def outline(self, username):
        if self._redis.sismember(self.SET_ALL_USERS, username):
            self._redis.srem(self.SET_ALL_USERS, username)
            self._redis.publish(self.SUBJECT_OUTLINE, username)

    def new_message(self, from_name, to_name, message):
        key = self.LIST_MESSAGES.format(from_=from_name, to=to_name)
        self._redis.rpush(key, message)

    def all_messages(self, from_name, to_name):
        key = self.LIST_MESSAGES.format(from_=from_name, to=to_name)
        return self._redis.lrange(key, 0, -1)

    def clear_messages(self, from_name, to_name):
        key = self.LIST_MESSAGES.format(from_=from_name, to=to_name)
        self._redis.delete(key)
