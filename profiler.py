# -*- coding: utf-8 -*-

import os
import time
import sqlite3
import urlparse

import wsgiref.simple_server as wsgi_server

_dbname = ':memory:'

con = sqlite3.connect(_dbname, check_same_thread=False, isolation_level=None)
con.execute('CREATE TABLE profiles(id INTEGER PRIMARY KEY AUTOINCREMENT, netloc TEXT, path TEXT, processtime FLOAT)')

def requestcounter(request, handler, chainfunc):
    def _(*args, **kw):
        start = time.time()
        chainfunc(*args, **kw)
        processtime = time.time() - start
        
        con.execute('INSERT INTO profiles(netloc, path, processtime) values(?, ?, ?)', (request.netloc, request.parsedpath, processtime))

    return _

class ProfileHandler:
    def __init__(self, request, match, config={}):
        self._handler = wsgi_server.ServerHandler(request.rfile, request.wfile, request.get_stderr(), request.get_environ())
        self._handler.request_handler = request
        self.config = config
        self.table = {'/view':self.view, '/clear':self.clear}

    def execute(self):
        self._handler.run(self.application)
    
    def application(self, env, start_response):
        path = self._handler.request_handler.parsedpath
        
        return self.table.get(path, self.notfound)(env, start_response)

    def notfound(self, env, start_response):
        start_response('404 NotFound', [('Content-Type', 'text/plain')])
        return '404 NotFound'

    def clear(self, env, start_response):
        con.execute('DELETE FROM profiles')
        start_response("200 OK", [('Content-Type','text/plain')])
        return "DELETED"

    def view(self, env, start_response):
        from StringIO import StringIO
        stdout = StringIO()

        params = {'order':'count DESC', 'limit':10}
        params.update(dict(map(lambda x: (x[0].lower(), x[1]), urlparse.parse_qsl(self._handler.request_handler.query))))
        
        query = 'SELECT netloc, path, count(id) AS count, avg(processtime) AS average from profiles GROUP BY path ORDER BY {order} LIMIT {limit}'.format(**params)
        cur = con.cursor()
        cur.execute(query)
        
        print >>stdout, query
        print >>stdout

        for row in cur:
	    print >>stdout, str("%s,%s,%s,%s" % (row[0],row[1],row[2],row[3]))

        cur.close()

        start_response("200 OK", [('Content-Type','text/plain')])

        return [stdout.getvalue()]
