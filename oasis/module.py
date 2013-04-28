# -*- coding: utf-8 -*-

import filters
import handlers

__localmodules = {'localfile': handlers.LocalFileHandler,
                'pipe': handlers.PipeHandler,
                'processtime': filters.processtime,
                'requestcounter': filters.requestcounter}

def localimport(modulename):
    parts = modulename.split('.')
    if len(parts) == 1:
        if parts[0] in __localmodules:
            return __localmodules[parts[0]]
        else:
            return __import__(parts[0])
    else:
        package, module, clsname = (parts[0], ".".join(parts[:-1]), parts[-1])
        return getattr(__import__(module, fromlist=[package]), clsname)
