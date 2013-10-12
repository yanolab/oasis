# -*- coding: utf-8 -*-

import datetime

# for request counter
_counter = {}


def processtime(request, chainfunc):
    """measure the execution time of processing."""

    def _(*args, **kw):
        start_at = datetime.datetime.now()
        chainfunc(*args, **kw)
        request.log_message('Time: %s in %s', datetime.datetime.now() - start_at, request.path)

    return _


def requestcounter(request, chainfunc):
    """count the number of requests"""

    def _(*args, **kw):
        count = _counter.get(request.path, 0)
        _counter[request.path] = count + 1
        request.log_message('%s is called %s times', request.path, count + 1)
        chainfunc(*args, **kw)

    return _
