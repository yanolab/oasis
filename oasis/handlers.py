# -*- coding: utf-8 -*-

import os
import sys
import ssl
import select
import socket
import shutil
import urllib
import urlparse
import posixpath
import mimetypes
import CGIHTTPServer
import wsgiref.handlers
import wsgiref.simple_server as wsgi_server

import module

class WSGIHandler(wsgi_server.WSGIRequestHandler):
    attributes = ['request', 'client_address', 'server', 'rfile',
                  'wfile', 'raw_requestline', 'command', 'path',
                  'headers', 'requestline', 'request_version']

    def __init__(self, request, match, config={}):
        self.config = config
        self.match = match

        for attr in self.attributes:
            setattr(self, attr, getattr(request, attr))

        self._handler = wsgi_server.ServerHandler(self.rfile, self.wfile, self.get_stderr(), self.get_environ())
        self._handler.request_handler = self
        self.application = module.localimport(self.config.get('app'))

    def execute(self):
        self._handler.run(self.application)


class PipeHandler(object):
    def __init__(self, request, match, config={}):
        self.request = request
        self.host = config.get('host', request.host)
        self.ssl = config.get('ssl', False)
        self.port = config.get('port', request.port)
        self._timeout = config.get('timeout', 30) * 10 # selectが0.1s刻みなので10倍しておく
        self.params = ('', '', request.parsedpath, request.params, request.query, '')
        self.config = config

    def _send(self, sock, msg):
        sock.send(msg)

    def execute(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.ssl:
            sock = ssl.wrap_socket(sock)

        try:
            sock.connect((self.host, self.port))
            self._send(sock, "%s %s %s\r\n" % (self.request.command, urlparse.urlunparse(self.params), self.request.request_version))
            self.request.headers['Connection'] = 'close'
            del self.request.headers['Proxy-Connection']
            for key_val in self.request.headers.items():
                self._send(sock, "%s: %s\r\n" % key_val)
            self._send(sock, "\r\n")

            self._pipe(sock)
        except socket.error, arg:
            self.request.send_error(500, 'connect failed to %s:%s, %s' % (self.host, self.port, arg))

    def _pipe(self, sock):
        timeout = 0
        while True:
            timeout += 1
            sockets, w, errors = select.select([self.request.connection, sock], [], [self.request.connection, sock], 0.1)

            if errors:
                break

            for s in (sockets or []):
                out = self.request.connection if s is sock else sock
                data = s.recv(4096)
                if data:
                    out.send(data)
                    timeout = 0

            if timeout >= self._timeout:
                break


class LocalFileHandler(object):
    def __init__(self, request, match, config={}):
        self.request = request
        self.path = config.get('path', request.parsedpath)
        self.config = config
        self.match = match

        if not mimetypes.inited:
            mimetypes.init()

    def execute(self):
        f = self.send_head()
        if f:
            self.copyfile(f, self.request.wfile)
            f.close()

    def send_head(self):
        fileobj = None

        path = self.config.get('path', None)
        if path:
            path = path.format(*self.match.groups(), **dict(path=self.path, **self.match.groupdict()))

        path = self.translate_path(path or self.path)
        self.request.log_message("Local-Path: %s", path)

        if os.path.isdir(path):
            self.request.send_response(301)
            self.request.send_header("Location", self.path + "/")
            self.request.end_headers()

        ctype = self.guess_type(path)

        try:
            fileobj = open(path, 'rb')
        except IOError:
            self.request.send_error(404, "File not found")
            return None

        self.request.send_response(200)
        self.request.send_header("Content-type", ctype)
        fs = os.fstat(fileobj.fileno())
        self.request.send_header("Content-Length", str(fs[6]))
        self.request.send_header("Last-Modified", self.request.date_time_string(fs.st_mtime))
        self.request.end_headers()
        return fileobj

    def translate_path(self, path):
        return _translate_path(self.config, path)

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        return mimetypes.types_map.get(ext.lower(), 'application/octet-stream')


class CGIHandler(CGIHTTPServer.CGIHTTPRequestHandler):
    attributes = ['request', 'client_address', 'server', 'rfile',
                  'wfile', 'raw_requestline', 'command',
                  'headers', 'requestline', 'request_version']

    def __init__(self, request, match, config={}):
        self.original_request = request
        self.path = config.get('path', request.parsedpath)
        self.config = config
        self.match = match

        for attr in self.attributes:
            setattr(self, attr, getattr(request, attr))

    def is_cgi(self):
        self.cgi_info = CGIHTTPServer._url_collapse_path_split(self.path)
        path = self.translate_path(self.path)
        if os.path.exists(path):
            return os.stat(path).st_mode & 0111 != 0
        return False

    def translate_path(self, path):
        return _translate_path(self.config, path)

    def execute(self):
        if self.is_cgi():
            self.run_cgi()
        else:
            LocalFileHandler(self.original_request, self.match, self.config).execute()


def _translate_path(config, path):
    path = path.split('?',1)[0]
    path = path.split('#',1)[0]
    path = posixpath.normpath(urllib.unquote(path))
    words = path.split('/')
    words = filter(None, words)
    path = config.get('root', os.getcwd())
    for word in words:
        drive, word = os.path.splitdrive(word)
        head, word = os.path.split(word)
        if word in (os.curdir, os.pardir): continue
        path = os.path.join(path, word)
    return path
