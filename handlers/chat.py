#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chat handlers.
"""

import time

import tornado.web
import tornado.gen
import tornado.concurrent
import tornado.escape
from tornado.ioloop import IOLoop

from libs.handler import BaseHandler
from libs.utils import active_authentication, json_multi_loads, \
    json_dumps, json_loads
from libs import robot


class ChatRoomHandler(BaseHandler):

    @active_authentication
    @tornado.gen.coroutine
    def get(self):
        username = self.current_user
        sql = 'select * from users where username=%s'
        user = yield self.async_task(self.db.get, sql, username)
        self.render('index.html', title=None, current_avatar=user.avatar)


class ChatHandler(BaseHandler):

    @active_authentication
    @tornado.gen.coroutine
    def post(self):
        self.future = self.msg_producer.wait_for_message()
        msg = yield self.future
        if not msg:
            return
        print('MSG: ', msg)
        channel, message = msg
        data = None
        if channel == self.rds.SUBJECT_ONLINE and message != self.current_user:
            sql = ('select username, avatar,'
                   'sex from users where username=%s')
            user = yield self.async_task(self.db.get, sql, message)
            data = {'type': 'online', 'message': user}
        elif channel == self.rds.SUBJECT_OUTLINE:
            data = {'type': 'outline', 'message': message}
        elif channel == self.rds.SUBJECT_NEW_MESSAGE:
            msg_j = json_loads(message)
            if msg_j['to'] == self.current_user:
                data = {
                    'type': 'message',
                    'message': {
                        'from': msg_j['from'],
                        'text': msg_j['text'],
                        'picture': msg_j['picture']
                    }
                }
        if data and not self.request.connection.stream.closed():
            self.write(tornado.escape.json_encode(data))
        else:
            return

    def on_connection_close(self):
        self.msg_producer.cancel_wait(self.future)


class UserLifeHandler(BaseHandler):
    """A long polling to indicate user if live."""

    WAIT_SECONDS = 3

    @active_authentication
    @tornado.gen.coroutine
    def post(self):
        self.rds.user_online(self.current_user, time.time())
        yield tornado.concurrent.Future()

    def on_connection_close(self):
        cur_ioloop = IOLoop.current()
        username = self.current_user
        # Given user a chance to reconnect soon.
        cur_ioloop.add_timeout(
            cur_ioloop.time() + self.WAIT_SECONDS,
            self.close_user_connection, username)

    def close_user_connection(self, username):
        timestamp = self.rds.get_user_online_timestamp(username)
        # If user reconnect quickly, treat it never offline.
        # Otherwise, the user offline too long , remove the user
        # and publish the user offline message.
        if timestamp and time.time() - timestamp > self.WAIT_SECONDS:
            self.rds.user_offline(username)


class UserListHandler(BaseHandler):

    @active_authentication
    @tornado.gen.coroutine
    def get(self):
        users = self.rds.all_online_users()
        if not users or len(users) <= 1:  # Doesn't include self
            self.write(tornado.escape.json_encode([]))
            return
        current_user = self.current_user
        users = ','.join([('"' + user + '"')
                         for user in users if user != current_user])
        sql = ('select username, avatar, sex from users '
               'where username in ({0})'.format(users))
        user_list = yield self.async_task(self.db.query, sql)
        self.write(tornado.escape.json_encode(user_list))


class MessageHandler(BaseHandler):
    """Handle mesages, if GET, return all messages, if POST,
    new message in.
    """

    @active_authentication
    def get(self):
        username = self.get_argument('username', None)
        me = self.current_user

        other_to_me = json_multi_loads(self.rds.all_messages(username, me))
        me_to_other = json_multi_loads(self.rds.all_messages(me, username))
        for d in other_to_me:
            d['self'] = False
        for d in me_to_other:
            d['self'] = True

        messages = sorted(other_to_me + me_to_other, key=lambda d: d['date'])
        self.write(tornado.escape.json_encode(messages))

    @active_authentication
    def post(self):
        to_name = self.get_argument('to', None)
        text = self.get_argument('text', None)
        picture = self.get_argument('picture', None)

        from_name = self.current_user
        message = {'text': text, 'picture': picture, 'date': time.time()}
        self.rds.new_message(from_name, to_name, json_dumps(message))
        pub_msg = {'from': from_name, 'to': to_name}
        pub_msg.update(message)
        self.rds.publish(self.rds.SUBJECT_NEW_MESSAGE, json_dumps(pub_msg))

        self.write('Got new message.')


class RobotHandler(BaseHandler):

    @active_authentication
    @tornado.gen.coroutine
    def post(self):
        message = self.get_argument('text', ' ')
        picture = self.get_argument('picture', None)
        me = self.current_user

        # Save message from me to Robot.
        human_msg = {'text': message, 'picture': picture, 'date': time.time()}
        self.rds.new_message(me, 'Robot', json_dumps(human_msg))

        sql = 'select id from users where username=%s'
        userid = yield self.async_task(self.db.get, sql, me)
        response = yield self.async_task(robot.get, message, userid)
        if picture:
            picture = '<b>不要发图片给我，亲！</b>'
        # Save message from Robot to me.
        robot_msg = {'text': response, 'picture': picture, 'date': time.time()}
        self.rds.new_message('Robot', me, json_dumps(robot_msg))
        # Publish message from Robot to me.
        pub_msg = {'from': 'Robot', 'to': me}
        pub_msg.update(robot_msg)
        self.rds.publish(self.rds.SUBJECT_NEW_MESSAGE, json_dumps(pub_msg))

        self.write('Got new message.')


urls = [
    ('/', ChatRoomHandler),
    ('/chat', ChatHandler),
    ('/user/live', UserLifeHandler),
    ('/user/list', UserListHandler),
    ('/messages', MessageHandler),
    ('/robot', RobotHandler),
]
