#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from optparse import OptionParser

from server import OasisServer, OasisRequestHandler

def main(args):
    """Start this server default on 127.0.0.1:8080"""

    configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default.json")

    parser = OptionParser()
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='print configuration.')
    parser.add_option('-c', '--config', dest='configfile', default=configfile, help='config file.')
    parser.add_option('-a', '--address', dest='address', default='127.0.0.1', help='server address.')
    parser.add_option('-p', '--port', dest='port', default=8080, type=int, help='server port.')

    (options, args) = parser.parse_args(args)

    with open(options.configfile) as f:
        config = json.load(f)

    httpd = OasisServer((options.address, options.port), OasisRequestHandler, config, options.verbose)

    print("Serving HTTP on %s port %s" % httpd.socket.getsockname())

    #httpd.handle_request()
    httpd.serve_forever()

if __name__ == '__main__':
    main(sys.argv[1:])
