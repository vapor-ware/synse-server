#!/usr/bin/env python
""" Testing utilities for the VaporCORE Southbound API tests

    Author:  Erick Daniszewski
    Date:    9/9/2015

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
from threading import Thread
from functools import wraps

import sys
import Queue


class TestThread(Thread):
    """ A thread class which executes a given function and gives back the execution end
    state (more specifically, whether or not an Exception is present on the thread's stack)
    of the thread in the specified bucket.
    """
    def __init__(self, func, bucket):
        super(TestThread, self).__init__()
        self.bucket = bucket
        self.func = func

    def run(self):
        try:
            # execute the function
            self.func()
        except Exception:
            # do nothing if function execution fails here, we want to catch
            # the exception in the thread executor by analyzing the results
            # of sys.exc_info()
            pass
        finally:
            # put the thread and and its exc_info on the queue
            self.bucket.put((self, sys.exc_info()))


class TestThreadExecutor(object):
    """ An executor of the TestThread class. It instantiates thread_count number of TestThreads,
    passing them the specified function to run as well as a Queue to hold system execution
    end state, and running each of those threads. Once a thread has executed the given function
    and put its end-state into the Queue, the executor will get the thread's end-state, analyze
    it to determine if an exception was thrown, and populate either True (no exception occurred)
    or False (exception occurred) into a result array, which is then returned.

    The result array can be validated to check if each thread executed successfully.

    Future improvements could check the exception type, however the current implementation
    cares only if the thread was successful or not.
    """
    def __init__(self, thread_count, func):
        self.thread_count = thread_count
        self.func = func

    def execute(self):
        bucket = Queue.Queue()
        join_list = []
        result = []
        test_threads = [TestThread(self.func, bucket) for _ in range(self.thread_count)]

        # start the threads
        for thread in test_threads:
            thread.start()

        while len(join_list) < self.thread_count:
            try:
                thread_obj, exc = bucket.get(block=False)
            except Queue.Empty:
                pass  # cannot exit, as the queue may be empty before any threads finish
            else:
                # exc can be broken into (exc_type, exc_obj, exc_trace) if we want more
                # control over what we do with the exception
                if exc == (None, None, None):
                    result.append(True)
                else:
                    result.append(False)
                join_list.append(thread_obj)

        for thread in join_list:
            thread.join()

        return result


def threaded(*args):
    """ Spawn multiple threads of a decorated function.

    The number of threads can be specified as an argument to the decorator,
    otherwise a default number of threads are spawned (default=25). The
    decorator can be used in the following forms::

       @threaded       <- spawns the default number of threads
       @threaded()     <- spawns the default number of threads
       @threaded(100)  <- spawns the given number of threads (100)
    """
    def _threaded(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(thread_count):
                t = Thread(target=func, args=args, kwargs=kwargs)
                t.setDaemon(True)
                t.start()
        return wrapper
    thread_count = 25  # default
    if len(args) == 1:
        if callable(args[0]):
            return _threaded(args[0])
        thread_count = args[0]
    return _threaded
