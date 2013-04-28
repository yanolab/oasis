#! /usr/bin/env python
# -*- coding: utf-8 -*-

__doc__ = """oasis is HTTP proxy and WSGI container and HTTPS support in a limited way.
oasis works on WSGIServer and ThreadingServer with python default module.
Python default WSGIServer is easy container, so this server is not fast.
I recomend to use for develop step on your application.
"""

__version__ = "0.1.0"

import re
import sys
import itertools
import datetime
import urlparse

from optparse import OptionParser

import wsgiref.simple_server as wsgi_server
import SocketServer as socket_server

import config

class HTTPRequestHandler(wsgi_server.WSGIRequestHandler):
    """
    This handler is created instance for each request.
    """

    server_version = "oasis/" + __version__

    rbufsize = 0

    def _init_request(self):
        """Initialize a request. Parse raw headers"""

        self.raw_requestline = self.rfile.readline()
        return self.parse_request()

    def handle(self):
        """
        This method handles a request.
        This handler is supported only http request, however fragment is not supported.
        """

        if not self._init_request():
            return

        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(self.path)
        self.scm = scm
        self.netloc = netloc
        self.host, self.port = (netloc+':80').split(':')[0:2]
        self.port = int(self.port)
        self.parsedpath = path
        self.params = params
        self.query = query
        self.fragment = fragment

        if not scm == 'http':
            self.send_error(400, "unsupported protocol : %s" % scm)
            return

        if fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return

        matches = config.forwards.get(netloc, {})

        inst = None

        for match in matches:
            m = match['match'].match(self.parsedpath)
            if m:
                cls = match.get('handler', config.default['handler'])
                handler = cls(self, m, match.get('config', {}))
                func = handler.execute
                break
        else:
            cls = config.default['handler']
            handler = cls(self, None, config.default['config'])
            func = handler.execute

        if hasattr(config, 'filters'):
            func = reduce(lambda chainfunc,filterfunc: filterfunc(self, handler, chainfunc), (func,) + config.filters)

        func()

class ThreadingWSGIServer(socket_server.ThreadingMixIn, wsgi_server.WSGIServer): pass

def compile_config():
    """Pre-compile your config file"""

    for key in config.forwards:
        for item in config.forwards[key]:
            item['match'] = re.compile(item['match'])

def print_config():
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    pp.pprint(config.forwards)

def main(server_address='127.0.0.1', port=8080):
    """Start this server default on 127.0.0.1:8080"""

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='print configuration.')

    (options, args) = parser.parse_args(sys.argv[1:])

    if options.verbose:
        print_config()

    compile_config()

    httpd = ThreadingWSGIServer((server_address, port), HTTPRequestHandler)

    print("Serving HTTP on %s port %s" % httpd.socket.getsockname())

    #httpd.handle_request()
    httpd.serve_forever()

if __name__ == '__main__':
    main ()
