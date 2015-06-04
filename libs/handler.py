#!/usr/bin/env python
# -*- coding: utf-8 -*-


import httplib

import tornado.web

from utils import AsyncTaskMixin


class BaseHandler(AsyncTaskMixin, tornado.web.RequestHandler):

    def get_current_user(self):
        username = self.get_secure_cookie('username')
        return username if username else None

    @property
    def db(self):
        return self.settings['db']

    @property
    def rds(self):
        return self.settings['rds']

    @property
    def msg_producer(self):
        return self.settings['msg_producer']

    def write_error(self, status_code, **kwargs):
        message = ''
        if status_code:
            message += str(status_code)
            reason = httplib.responses.get(status_code, None)
            if reason:
                message += ' ' + reason + '.'
            else:
                message += ' Unknown Error.'
        else:
            # Doesn't display kwargs["ex_info"]
            message = '500 Internal Server Error.'
        self.render('error.html', message=message)


class DefaultHandler(tornado.web.RequestHandler):

    def get(self):
        self.render('error.html', message='Nothing For You.')
