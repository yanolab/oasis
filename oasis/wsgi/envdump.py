# -*- coding: utf-8 -*-

from StringIO import StringIO

def application(env, start_response):
    stdout = StringIO()

    h = env.items()
    h.sort()

    for k,v in h:
        print >>stdout, k,'=', repr(v)

    start_response("200 OK", [('Content-Type','text/plain')])

    return [stdout.getvalue()]
