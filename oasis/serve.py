#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse

from server import OasisServer, OasisRequestHandler


def main(args):
    """Start this server default on 127.0.0.1:8080"""

    parser = argparse.ArgumentParser(description="oasis")
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true', help='print configuration.')
    parser.add_argument('-c', '--config', dest='configfile',
                        type=argparse.FileType('r'), default=None, help='config file.')
    parser.add_argument('-a', '--address', dest='address',
                        default='127.0.0.1', help='server address.')
    parser.add_argument('-p', '--port', dest='port',
                        default=8080, type=int, help='server port.')

    options = parser.parse_args(args)

    if options.configfile:
        print("loading your configration file %s" % options.configfile.name)
        config = json.load(options.configfile)
    else:
        import default
        config = json.loads(default.json)

    httpd = OasisServer((options.address, options.port),
                        OasisRequestHandler,
                        config, options.verbose)

    print("Serving HTTP on %s port %s" % httpd.socket.getsockname())

    httpd.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])
