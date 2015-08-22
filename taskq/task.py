# -*- coding: utf-8 -*-

from __future__ import print_function, division

import os
import uuid
import imp
import inspect
import time
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

from utils import dumps, ClassUnpickler


class Task(object):
    """Task object is an encapsulation of callalbe. The class has
    implemented pickle protocol.

    Callable can be builtin funtion, funtion, method and instance
    callable.
    """

    def __init__(self, callable, args=None, kwargs=None):
        self._callable = callable
        if not args:
            args = ()
        self._args = args
        if not kwargs:
            kwargs = dict()
        self._kwargs = kwargs
        self._created = time.time()
        self._tid = None

    def execute(self):
        return self._callable(*self._args, **self._kwargs)

    @property
    def id(self):
        if self._tid is None:
            self._tid = uuid.uuid4().hex
        return self._tid

    @id.setter
    def id(self, task_id):
        if self._tid is None:
            self._tid = task_id
        else:
            raise ValueError('"id" already exists!')

    @property
    def callable(self):
        return self._callable

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    def __getstate__(self):
        file_path, module_name = None, None
        instance, callable_name, cls_name = None, None, None
        if inspect.isfunction(self._callable):
            callable_name = self._callable.__name__
            file_path = inspect.getsourcefile(self._callable)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
        elif inspect.isbuiltin(self._callable):
            callable_name = self._callable.__name__
            module_name = 'builtin'
        elif inspect.ismethod(self._callable):
            file_path = inspect.getsourcefile(self._callable)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            cls_name = self._callable.__self__.__class__.__name__
            instance = dumps(self._callable.__self__)
            callable_name = self.callable.__name__
        # instance callable
        elif (not inspect.isclass(self._callable) and
              hasattr(self._callable, '__call__')):
            file_path = inspect.getsourcefile(self._callable.__call__)
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            cls_name = self._callable.__class__.__name__
            instance = dumps(self._callable)
            callable_name = '__call__'
        return (self._tid, file_path, module_name, cls_name, instance,
                callable_name, self._args, self._kwargs, self._created)

    def __setstate__(self, state):
        (self._tid, file_path, module_name, cls_name, instance,
         callable_name, self._args, self._kwargs, self._created) = state
        # builtin function or function
        if instance is None:
            if module_name == 'builtin':
                module = builtins
            else:
                module = imp.load_source(module_name, file_path)
            self._callable = getattr(module, callable_name)
        # method or instance callable
        else:
            module = imp.load_source(module_name, file_path)
            cls = getattr(module, cls_name)
            with ClassUnpickler(instance, cls) as unpickler:
                instance = unpickler.load()
            #  instance = loads(instance)
            self._callable = getattr(instance, callable_name)
