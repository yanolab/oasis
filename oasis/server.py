# -*- coding: utf-8 -*-

__doc__ = """oasis is HTTP proxy and WSGI container and HTTPS support in a limited way.
oasis works on WSGIServer and ThreadingServer with python default module.
Python default WSGIServer is easy container, so this server is not fast.
I recomend to use for develop step on your application.
"""

__version__ = "0.1.0"

import re
import copy
import pprint
import urlparse
import wsgiref.simple_server as wsgi_server
import SocketServer as socket_server

import module

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

    def _find_handler(self, envs):
        for env in envs:
            matched = env['route'].match(self.parsedpath)
            if matched:
                handler = env['handler'](self, matched, env.get('config', {})).execute
                if 'hooks' in env:
                    return reduce(lambda first, second: second(self, first), [handler] + env['hooks'])
        return None

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

        if not scm in ['', 'http']:
            self.send_error(400, "unsupported protocol : %s" % scm)
            return

        if fragment:
            self.send_error(400, "fragment is not supported - %s" % self.path)
            return

        envs = self.server.config['apps'].get(netloc, None) or self.server.config['apps'].get('*')

        handler = lambda : self.log_message("cannot found handler.")

        if type(envs) == list or type(envs) == tuple:
            handler = self._find_handler(envs)
        elif type(envs) == dict:
            handler = self._find_handler([envs])

        if 'hooks' in self.server.config:
            handler = reduce(lambda first, second: second(self, first), [handler] + self.server.config['hooks'])

        handler()


class ThreadingWSGIServer(socket_server.ThreadingMixIn, wsgi_server.WSGIServer):
    def __init__(self, server_address, cls, config, debug=False):
        wsgi_server.WSGIServer.__init__(self, server_address, cls)
        self.config = self._precompile(config)

        if debug:
            self._printconfig(config)

    def _printconfig(self, config):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(config)

    def _precompile(self, config):
        """pre-compile config file"""
        copied = copy.deepcopy(config)
        for netloc in copied['apps']:
            env = copied['apps'][netloc]
            env['route'] = re.compile(env['route'])
            env['handler'] = module.localimport(env['handler'])
            if 'hooks' in env:
                env['hooks'] = [module.localimport(hook) for hook in env['hooks']]

        copied['hooks'] = [module.localimport(hook) for hook in copied.get('hooks', [])]

        return copied
