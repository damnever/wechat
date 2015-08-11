# -*- coding: utf-8 -*-

import os
import importlib
import pkgutil


def load_urls(urls=None, attr='urls'):
    if urls is None:
        urls = list()
    # pkg_name = os.path.dirname(__file__)
    pkg_path = os.path.abspath(os.path.dirname(__file__))
    pkg_name = os.path.basename(pkg_path)

    for _, name, ispkg in pkgutil.iter_modules([pkg_path]):
        if ispkg:
            continue
        module = importlib.import_module('.'+name, pkg_name)
        urls.extend(getattr(module, attr))

    return urls

urls = load_urls()
