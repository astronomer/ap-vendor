#!/usr/bin/env python3
from urllib import request

req = request.Request("http://127.0.0.1:8000/quitquitquit", method="POST")
request.urlopen(req)
