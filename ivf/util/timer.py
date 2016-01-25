
# -*- coding: utf-8 -*-
## @package ivf.util.timer
#
#  Timer class, functions.
#  @author      tody
#  @date        2015/07/29

import time


class Timer(object):
    def __init__(self, timerName, logger=None):
        self._name = timerName
        self._logger = logger
        self._start = time.time()

    def start(self):
        self._start = time.time()

    def stop(self):
        self._end = time.time()
        self._secs = self._end - self._start
        self._msecs = self._secs * 1000  # millisecs

    def secs(self):
        return self._secs

    def msecs(self):
        return self._msecs

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *args):
        self.stop()

        self.secStr = "%s: %f s" % (self._name, self._secs)
        self.msecStr = "%s: %f ms" % (self._name, self._msecs)

        if self._logger is not None:
            self._logger.debug(self.secStr)

        else:
            print self.secStr

    def __str__(self):
        return self.secStr


def timing_func(func=None, timerName=None, logger=None):
    def _decorator(func):
        _timerName = timerName
        if timerName is None:
            _timerName = func.__name__

        import functools

        @functools.wraps(func)
        def _with_timing(*args, **kwargs):

            with Timer(_timerName, logger) as t:
                ret = func(*args, **kwargs)

            return ret
        return _with_timing

    if func:
        return _decorator(func)
    else:
        return _decorator
