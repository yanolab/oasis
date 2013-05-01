# -*- coding: utf-8 -*-

json = """{
  "apps":{
    "":[{"route":["/cgi-bin", "/htbin"], "handler":"cgi"},
        {"route":"/wsgi", "handler":"wsgi", "config":{"app":"oasis.wsgi.envdump.application"}},
        {"route":"/", "handler":"localfile"}],
    "*":{"route":"/", "handler":"pipe"}
  },
  "hooks":["processtime", "requestcounter"]
}"""
