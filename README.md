oasis
=====
A simple HTTP, PROXY, CGI, WSGI server

Requirements
------------
* Python 2.7 or later (not support 3.x)

Status
------
[![Build Status](https://travis-ci.org/yanolab/oasis.png?branch=master)](https://travis-ci.org/yanolab/oasis)

Features
--------
* HTTP(Limited HTTPS)
* Proxy
* CGI
* WSGI

Installation
------------
If you can use stable version of oasis, run the following command.

    $ pip install oasis

You want to use latest version, you can use git clone from github.com.

    $ git clone https://github.com/yanolab/oasis.git
    $ cd oasis
    $ sudo python setup.py install

How to use
----------
Run the following command and See the help.

    $ python -m oasis.serve -h
    usage: python -m oasis.serve [-h] [-v] [-c CONFIGFILE] [-a ADDRESS] [-p PORT]

    oasis

    optional arguments:
        -h, --help            show this help message and exit
        -v, --verbose         print configuration.
        -c CONFIGFILE, --config CONFIGFILE
                              config file.
        -a ADDRESS, --address ADDRESS
                              server address.
        -p PORT, --port PORT  server port.


Configuration
-------------
Configuration is JSON format. Default configuration is there.
```json
{
  "apps":{
    "":[{"route":["/cgi-bin", "/htbin"], "handler":"cgi"},
        {"route":"/wsgi", "handler":"wsgi", "config":{"app":"oasis.wsgi.envdump.application"}},
        {"route":"/", "handler":"localfile"}],
    "*":{"route":"/", "handler":"pipe"}
  },
  "hooks":["processtime", "requestcounter"]
}
```

You must write your configuration under "apps".
'""' means 127.0.0.1, and '"*"' means any domain.
If you want proxy the specification domain, write domain on there. For example `"www.google.com": {"route":"/", "handler":"localfile"}` is any request for www.google.com to local file.
Handler is the only one on each route. Handlers are localfile(WWW), pipe(PROXY), cgi, wsgi.
Global hooks is under "hooks". Each route can have "hook".
If you want to use your handler, write your script import path on "handler".

History
-------
0.9.0 (2013-5-7)
~~~~~~~~~~~~~~~~~~
* first release
