# -*- coding: utf-8 -*-


from __future__ import print_function, division

import argparse
import multiprocessing

from worker import Worker
from utils import enable_pretty_logging
from connection import Connection


def main():
    url, max_workers, retry = parse_args()
    enable_pretty_logging()
    connection = Connection.use_connection(url or read_url())
    worker = Worker(connection, max_workers, retry)
    try:
        worker.run()
    except KeyboardInterrupt:
        worker.stop()
        worker.report()


def read_url():
    url = 'redis://localhost/0'
    with open('./connection.config', 'r') as f:
        url = f.readline()
    return url.strip('\n')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--redis_url', default=None,
                        help='Given a url to initialize Redis.')
    parser.add_argument('-m', '--max_workers', type=int,
                        default=multiprocessing.cpu_count(),
                        help='The max workers for process pool.')
    parser.add_argument('-r', '--retry', type=int, default=1,
                        help='The number of fail task should try.')
    args = parser.parse_args()
    return args.redis_url, args.max_workers, args.retry


if __name__ == '__main__':
    main()
