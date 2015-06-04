#!/usr/bin/env python
# -*- coding: utf-8 -*-


import torndb


def connect(host, database, user, password, **kwargs):
    """Connect to MySQL."""
    # kwargs['cursorclass'] = MySQLdb.cursors.DictCursor
    db = torndb.Connection(host, database, user, password, **kwargs)
    return db
