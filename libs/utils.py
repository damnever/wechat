#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import functools
import hashlib
import uuid
import urlparse
import urllib

from tornado.web import HTTPError
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor


def active_authentication(method):
    """Decorate method withs this to require that the user be logged in,
    and make sure the email of user is already verified.

    If user is not logged in and not active, they will be redirected to
    the login url.
    """
    @functools.wraps(method)
    def _wrapper(self, *args, **kwargs):
        redirect = False
        if not self.current_user:
            redirect = True
        else:
            sql = 'select * from users where username=%s'
            user = self.db.get(sql, self.current_user)
            if not user.active:
                redirect = True
        if redirect:
            if self.request.method in ('GET', 'HEAD'):
                url = self.get_login_url()
                if '?' not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += '?' + urllib.urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return _wrapper


def join_path(current_file, fpath):
    """Making path absolute."""
    return os.path.join(os.path.dirname(current_file), fpath)


# A list of JSON(or str-like JSON) object operation.
def json_loads(s):
    return json.loads(s)

def json_multi_loads(strs):
    return [json.loads(s) for s in strs]

def json_dumps(j):
    return json.dumps(j)

def json_multi_dumps(jsons):
    return [json.dumps(j) for j in jsons]


def gen_token():
    """Generating token, which will be used for email verification,
    or password changing request.
    """
    return uuid.uuid4().hex


def encrypt_password(password):
    """Encrypting password by sha1 with some change."""
    mid = ''.join([hex(ord(w))[2:] for w in password])
    return hashlib.sha1(mid).hexdigest()


def parse_configure_file(options, define, path):
    """Parse  global options from a config file, which is different
    from `tornado.options.parse_config_file`, if name doesn't define,
    the function will define it.

    See:
    https://bitbucket.org/felinx/poweredsites/src/6040f8cf119ca530c9359275f3beaf63d5fc441d/poweredsites/libs/utils.py?at=default
    """
    config = {}
    execfile(path, config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, default=config[name])


class AsyncTaskMixin(object):
    """Making a synchronous method asynchronously on a executor.

    The `IOLoop` and executor to be used are determined by the
    `io_loop` and `executor` attributes of `self`.

    References: https://gist.github.com/methane/2185380
    """
    MAX_WORKERS = 10
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def async_task(self, callback, *args, **kwargs):
        result = callback(*args, **kwargs)
        return result
