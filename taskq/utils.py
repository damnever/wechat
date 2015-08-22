# -*- coding: utf-8 -*-

"""
Logging support with colors, just available in *unix.
Borrow from `tornado.log`:
    https://github.com/tornadoweb/tornado/blob/master/tornado/log.py
"""

from __future__ import print_function, division

import sys
import functools
import logging
import logging.handlers
try:
    import curses
except ImportError:
    curses = None
#  try:
    #  import cPickle as pickle
#  except ImportError:
import pickle
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


logger = logging.getLogger("TASKQ")

dumps = functools.partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL)
loads = pickle.loads


class NoSuchIdExists(Exception):
    pass


class ClassUnpickler(object):
    """This class aim to resolve pickle.Unpickler.find_class.
    And it implement context manager protocol, `as` substatement
    return a Unpickler object initialize by StringIO buffer.

    ```
    with Unpicle(s) as unpickler:
        obj = unpickler.load()
    ```
    """

    def __init__(self, buffer, cls):
        self._f = StringIO(buffer)
        self._cls = cls

    def __enter__(self):
        def _resolve_class(module, name):
            return self._cls
        unpickler = pickle.Unpickler(self._f)
        unpickler.find_class = _resolve_class
        return unpickler

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if hasattr(self, '_f'):
            self._f.close()


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


def enable_pretty_logging(log_level="info", logger=logger):
    logger.setLevel(getattr(logging, log_level.upper()))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(LogFormatter())
    logger.addHandler(stream_handler)


class LogFormatter(logging.Formatter):

    DEFAULT_FORMAT = "%(color)s[%(levelname)1.1s %(asctime)s]%(end_color)s %(message)s"
    DEFAULT_DATE_FORMAT = "%y-%m-%d %H:%M:%S"
    DEFAULT_COLORS = {
        logging.DEBUG: 4,  # Blue
        logging.INFO: 2,  # Green
        logging.WARNING: 3,  # Yellow
        logging.ERROR: 1,  # Red
    }

    def __init__(self, color=True, fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT,
                 colors=DEFAULT_COLORS):
        logging.Formatter.__init__(self, datefmt=datefmt)
        self._fmt = fmt

        self._colors = {}
        if color and _stderr_supports_color():
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            for levelno, code in colors.items():
                self._colors[levelno] = unicode(curses.tparm(fg_color, code),
                                                "ascii")
            self._normal = unicode(curses.tigetstr("sgr0"), "ascii")
        else:
            self._normal = ""

    def format(self, record):
        try:
            message = record.getMessage()
            assert isinstance(message, basestring)
            record.message = _safe_unicode(message)
        except Exception as e:
            record.message = "Bad message (%s): %r" % (e, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)

        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ""

        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            lines = [formatted.rstrip()]
            lines.extend(_safe_unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)

        return formatted.replace('\n', '\n    ')


def _stderr_supports_color():
    color = False
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:
            pass
    return color


def _safe_unicode(s):
    if isinstance(s, (unicode, type(None))):
        return s
    if not isinstance(s, bytes):
        raise TypeError("Excepted bytes, unicode, None; got %r" % type(s))
    try:
        return s.decode("utf-8")
    except UnicodeDecodeError:
        return repr(s)


if __name__ == "__main__":
    enable_pretty_logging()
    print(_stderr_supports_color())
    print(hasattr(sys.stderr, 'isatty'))
    print(curses)
    try:
        1 / 0
    except ZeroDivisionError:
        # logger.error("error", exc_info=sys.exc_info())
        logger.error("error", exc_info=True)
