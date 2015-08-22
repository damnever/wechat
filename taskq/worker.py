# -*- coding: utf-8 -*-


from __future__ import print_function, division

import time
import multiprocessing

#  import concurrent.futures

import tqueue
from utils import logger


class Worker(object):
    """Use `concurrent.futures` provides asynchronous execution.
    """

    MAX_WORKERS = multiprocessing.cpu_count()

    def __init__(self, connection, max_workers=MAX_WORKERS, retry=1):
        self._conn = connection
        self._max_workers = max_workers
        self._retry = retry

        #  self._future_task_map = dict()
        self._retry_count = dict()
        self._queue = tqueue.Queue()
        self._success_queue = tqueue.SuccessQueue()
        self._fail_queue = tqueue.FailQueue()
        self._dead_queue = tqueue.DeadQueue()
        self._run = False
        self._start_time = time.time()
        self._empty = False
        self._print("[+] ", "Taskq starting ...")

    def run(self):
        self._run = True
        while self._run:
            if self._queue.size() == 0:
                # If wait Queue is empty and retry count less than `_retry`,
                # execute tasks from FailQueue, else push to DeadQueue.
                if self._retry > 0 and self._fail_queue.size() != 0:
                    task_id, task_raw, task, exc_info = self._fail_queue.dequeue()
                    retry_count = self._retry_count.get(task_id, 0)
                    # Retry count is out of limit.
                    if retry_count >= self._retry:
                        self._dead_queue.enqueue(task_id, exc_info)
                        logger.warning("Task #{0} is dead!".format(task_id))
                        continue
                    self._retry_count[task_id] = retry_count + 1
                    logger.info("Retry task: {0}".format(task.callable))
                # All queues is empty or does not need retry,
                # report results.
                else:
                    if self.no_task_in_ten_seconds() and not self._empty:
                        self.report()
                        self._empty = True
                    time.sleep(1)
                    continue
            # Execute normal task.
            else:
                self._empty = False
                task_id, task_raw, task = self._queue.dequeue()
                logger.info("Try task: {0}".format(task.callable))
            try:
                result = task.execute()
            except Exception as e:
                err_msg = '{0}: {1}'.format(type(e).__name__, e.args)
                retry_count = self._retry_count.get(task_id, 0)
                if self._retry > 0 and retry_count < self._retry:
                    self._fail_queue.enqueue(task_id, task_raw, err_msg)
                else:
                    self._dead_queue.enqueue(task_id, err_msg)
                logger.error("Execute task: #{0} got {1}".format(task_id, err_msg))
            else:
                self._success_queue.enqueue(task_id, result)
                logger.info("Task #{0} done! Got: {1}".format(task_id, result))
            self.reset_time()

    def stop(self):
        self._print("\n[+] ", "Taskq stoping ...")
        #  for future in self._future_task_map:
            #  future.cancel()
        #  del self._future_task_map
        del self._retry_count
        self._run = False

    def no_task_in_ten_seconds(self):
        if time.time() - self._start_time >= 10:
            return True
        return False

    def reset_time(self):
        self._start_time = time.time()

    def report(self):
        self._print('', '=' * 23)
        print(' Success tasks: {0}'.format(self._success_queue.size()))
        if self._retry:
            failed = self._dead_queue.size()
        else:
            failed = self._fail_queue.size()
        print(' Fail tasks: {0}'.format(failed))
        self._print('', '=' * 23)

    def _print(self, pre='', msg=''):
        print(u"\x1b[01m{0}\x1b[39;49;00m"
              "\x1b[33;01m{1}\x1b[39;49;00m".format(pre, msg))
