# -*- coding: utf-8 -*-

import time
import urllib
import unittest
import threading
from functools import partial

from oasis.server import OasisServer, OasisRequestHandler


class ServerTest(unittest.TestCase):
    def _serve_on_request(self, config):
        httpd = OasisServer(("127.0.0.1", 8080), OasisRequestHandler, config, False)
        httpd.handle_request()

    def testLocalFile(self):
        config = {"apps": {"": {"route":"/", "handler": "localfile"}}}

        th = threading.Thread(target=partial(self._serve_on_request, config))
        th.start()
        time.sleep(1)

        res = urllib.urlopen("http://127.0.0.1:8080/README.md")

        self.assertEqual(res.getcode(), 200, "status code must be 200")
        res.read()
        res.close()

        th.join()

    def testWSGI(self):
        config = {"apps": {"": {"route":"/", "handler": "wsgi", "config": {"app": "oasis.wsgi.envdump.application"}}}}

        th = threading.Thread(target=partial(self._serve_on_request, config))
        th.start()
        time.sleep(1)

        res = urllib.urlopen("http://127.0.0.1:8080/wsgi")

        self.assertEqual(res.getcode(), 200, "status code must be 200")
        res.read()
        res.close()

        th.join()

    def testPIPE(self):
        config = {"apps": {"*": {"route":"/", "handler": "pipe"}}}

        th = threading.Thread(target=partial(self._serve_on_request, config))
        th.start()
        time.sleep(1)

        res = urllib.urlopen("http://yanolab.github.io/", proxies={"http":"http://127.0.0.1:8080"})

        self.assertEqual(res.getcode(), 200, "status code must be 200")
        res.read()
        res.close()

        th.join()

    def testCGI(self):
        config = {"apps": {"*": {"route":"/", "handler": "cgi"}}}

        th = threading.Thread(target=partial(self._serve_on_request, config))
        th.start()
        time.sleep(1)

        cginame = "hello.cgi"
        with open(cginame, "w") as f:
            f.write("#! /usr/bin/env python\n\n")
            f.write("print 'Content-Type: text/plain\\n\\n'\n")
            f.write("print 'hello'")

        import os
        os.chmod(cginame, 0777)

        res = urllib.urlopen("http://127.0.0.1:8080/%s" % cginame)

        self.assertEqual(res.getcode(), 200, "status code must be 200")
        res.read()
        res.close()

        th.join()
        os.remove(cginame)

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(ServerTest))
    return suite
