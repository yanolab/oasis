# -*- coding: utf-8 -*-

import datetime

def processtime(request, handler, chainfunc):
    def _(*args, **kw):
        start_at = datetime.datetime.now()
        chainfunc(*args, **kw)
        request.log_message('process time: %s for %s', datetime.datetime.now() - start_at, request.path)

    return _

_counter = {}
def requestcounter(request, handler, chainfunc):
    def _(*args, **kw):
        count = _counter.get(request.path, 0)
        _counter[request.path] = count + 1
        request.log_message('called %s times for %s', count + 1, request.path)

        chainfunc(*args, **kw)

    return _

