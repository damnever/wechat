#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options

from libs.message import MessageProducter
from libs.utils import parse_configure_file, join_path
from models import mysql, rds
from taskq.connection import Connection


define('port', default=8888, help='run on the given port', type=int)


class Application(tornado.web.Application):

    def __init__(self):
        from handlers import urls
        from libs.handler import DefaultHandler

        db = mysql.connect(
            options.db_host, options.db_database,
            options.db_user, options.db_passwd
        )

        settings = {
            'static_path': join_path(__file__, 'static'),
            'template_path': join_path(__file__, 'templates'),
            'cookie_secret': options.cookie_secret,
            'xsrf_cookies': options.xsrf_cookies,
            'login_url': options.login_url,
            'debug': options.debug,
            'default_handler_class': DefaultHandler,
            'db': db,
            'rds': rds.Rds(),
            'msg_producer': MessageProducter(),
        }
        tornado.web.Application.__init__(self, urls, **settings)


def run_server():
    # For task queue
    Connection.setup(db=3)
    parse_configure_file(options, define, join_path(__file__, './chat.conf'))
    options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(
        Application(), xheaders=options.xheaders)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run_server()
