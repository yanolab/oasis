# -*- coding: utf-8 -*-

import datetime

def processtime(request, chainfunc):
    def _(*args, **kw):
        start_at = datetime.datetime.now()
        chainfunc(*args, **kw)
        request.log_message('Time: %s in %s', datetime.datetime.now() - start_at, request.path)
    return _

_counter = {}
def requestcounter(request, chainfunc):
    def _(*args, **kw):
        count = _counter.get(request.path, 0)
        _counter[request.path] = count + 1
        request.log_message('%s is called %s times', request.path, count + 1)
        chainfunc(*args, **kw)
    return _

