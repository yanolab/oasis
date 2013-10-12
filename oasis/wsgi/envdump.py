# -*- coding: utf-8 -*-

import sys

if sys.version_info[0] >= 3:
    from io import StringIO
else:
    from StringIO import StringIO


def application(env, start_response):
    stdout = StringIO()

    h = list(env.items())
    h.sort()

    for k, v in h:
        stdout.write("{0}={1}\n".format(k, repr(v)))

    start_response("200 OK", [('Content-Type', 'text/plain')])

    return [stdout.getvalue()]
