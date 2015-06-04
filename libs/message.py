#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import threading

from tornado.concurrent import Future

from models.rds import Rds


class MessageProducter(object):
    """The object to yield(subscribe) message from redis publisher."""

    def __init__(self):
        self._waiters = set()
        # Rds object is singleton.
        self._rds = Rds()

        # Yield message forever, always waiting redis publish message.
        msg_thread = threading.Thread(target=self._yield_message, args=())
        msg_thread.daemon = True
        msg_thread.start()

    def wait_for_message(self):
        result_future = Future()
        self._waiters.add(result_future)
        return result_future

    def cancel_wait(self, future):
        if future in self._waiters:
            self._waiters.remove(future)
            # Set an empty result to unblock any coroutines waiting.
            future.set_result([])

    def _yield_message(self):
        while 1:
            message = self._rds.get_message()
            if message:
                self._notify_waiters((message['channel'], message['data']))
            time.sleep(0.0001)

    def _notify_waiters(self, message):
        for future in self._waiters:
            future.set_result(message)
        self._waiters= set()
