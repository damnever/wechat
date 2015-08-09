#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User handlers.
"""

from __future__ import print_function

import base64

import tornado.gen
from tornado.web import HTTPError
from tornado.options import options

from libs import mail
from libs.handler import BaseHandler
from libs.utils import encrypt_password, gen_token


class SginupHandler(BaseHandler):

    def get(self):
        self.render('signup.html', title='注册')

    @tornado.gen.coroutine
    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        # repasswd = self.get_argument('repassword', None)
        email = self.get_argument('email', None)
        sex = self.get_argument('sex', None)
        avatar = self.request.files['avatar'][0]

        encrypted = encrypt_password(password)
        b64avatar = base64.b64encode(avatar['body'])

        sql = """insert into `users`(username, password, email, sex, avatar)
        values (%s, %s, %s, %s, %s)"""
        yield self.async_task(self.db.insert,
                              sql, username, encrypted, email, sex, b64avatar)
        # Send confirm email and redirect to email link
        token = gen_token()
        url = '{0}://{1}/verify/{2}'.format(
            self.request.protocol, self.request.host, token)
        subject = mail.SIGNUP_SUBJECT
        message = mail.SIGNUP_MESSAGE.format(name=username, url=url)
        from_addr = options.from_addr
        from_pwd = options.from_pwd
        smtp_server = options.smtp_server
        yield self.async_task(mail.send_email, from_addr, from_pwd, username,
                              email, message, subject, smtp_server)
        # Insert into table and wait to verify
        sql = 'insert into `verify` (token, username) values (%s, %s)'
        yield self.async_task(self.db.insert, sql, token, username)
        self.render("mail.html", username=username, message="注册成功")


class LoginHandler(BaseHandler):

    def get(self):
        self.render('login.html', title='登录')

    def post(self):
        if self.current_user:
            self.redirect('/')
        else:
            self.get()


class CheckPasswordHandler(BaseHandler):

    @tornado.gen.coroutine
    def post(self):
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        remember = self.get_argument('remember', None)
        sql = 'select * from users where email=%s'
        user = yield self.async_task(self.db.get, sql, email)
        if encrypt_password(password) == user.password:
            self.write('ok')
            if remember and remember=='remember':
                self.set_secure_cookie('username', user.username, 7)
            self.set_secure_cookie('username', user.username, 1)
            return
        self.write('fail')


class CheckUsernameHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self):
        username = self.get_argument('username', None)
        sql = 'select * from users where username=%s'
        user = yield self.async_task(self.db.get, sql, username)
        if user or username == 'Robot':
            self.write('fail')
            return
        self.write('ok')


class CheckEmailHandler(BaseHandler):

    @tornado.gen.coroutine
    def post(self):
        check = self.get_argument('check', None)
        email = self.get_argument('email', None)
        sql = 'select * from users where email=%s'
        user = yield self.async_task(self.db.get, sql, email)
        # If check, signup, else login.
        if user:
            if check:
                self.write('fail')
                return
            else:
                # Check user email if verified.
                self.write('ok' if user.active else 'not')
                return
        else:
            self.write('ok' if check else 'fail')


class ConfirmEmailHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self, token):
        sqlq = 'select * from verify where token=%s'
        verified = yield self.async_task(self.db.get, sqlq, token)
        if verified:
            username = verified.username
            sqlu = 'update users set active=1 where username=%s'
            yield self.async_task(self.db.update, sqlu, username)
            sqld = 'delete from verify where token=%s and username=%s'
            yield self.async_task(self.db.update, sqld, token, username)
            self.render('verified.html', username=username)
        else:
            raise HTTPError(404)


class FindPasswdHandler(BaseHandler):

    def get(self):
        self.render('findpw.html', title='密码找回')

    @tornado.gen.coroutine
    def post(self):
        email = self.get_argument('email', None)
        sql = 'select * from users where email=%s'
        user = yield self.async_task(self.db.get, sql, email)

        token = gen_token()
        url = '{0}://{1}/changepassword/{2}'.format(
            self.request.protocol, self.request.host, token)
        subject = mail.FINDPW_SUBJECT
        message = mail.FINDPW_MESSAGE.format(name=user.username, url=url)
        from_addr = options.from_addr
        from_pwd = options.from_pwd
        smtp_server = options.smtp_server
        yield self.async_task(mail.send_email, from_addr, from_pwd, user.username,
                              email, message, subject, smtp_server)
        # Insert into table
        sql = 'insert into `losspw` (token, username) values (%s, %s)'
        yield self.async_task(self.db.insert, sql, token, user.username)
        self.render("mail.html",
                    username=user.username, message="您的密码更改请求已接受")


class ChangePasswordHandler(BaseHandler):

    @tornado.gen.coroutine
    def get(self, token):
        sql = 'select * from losspw where token=%s'
        lossed = yield self.async_task(self.db.get, sql, token)
        if lossed:
            self.render("changepw.html", title="更改密码", username=lossed.username)
        else:
            raise HTTPError(404)

    @tornado.gen.coroutine
    def post(self, token):
        username = self.get_argument('username', None)
        password = self.get_argument("password", None)
        encrypted = encrypt_password(password)
        sqlu = 'update users set password=%s where username=%s'
        yield self.async_task(self.db.update, sqlu, encrypted, username)
        sqld = 'delete from losspw where token=%s and username=%s'
        yield self.async_task(self.db.update, sqld, token, username)
        self.render('pwchanged.html', username=username)


urls = [
    ('/login/', LoginHandler),
    ('/signup/', SginupHandler),
    ('/checkpassword', CheckPasswordHandler),
    ('/checkusername', CheckUsernameHandler),
    ('/checkemail', CheckEmailHandler),
    ('/confirmemail', ConfirmEmailHandler),
    ('/findpassword/', FindPasswdHandler),
    ('/verify/(.*?)', ConfirmEmailHandler),
    ('/changepassword/(.*?)', ChangePasswordHandler),
]
