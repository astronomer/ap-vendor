#!/usr/bin/env python3
"""Launch vector in a subprocess and handle web signaling for the sidecar."""
import os
import subprocess
from http import server

ppid = os.getppid()


# The below process would be a call to vector, but it is a date loop just for demonstration
proc = subprocess.Popen("/usr/local/bin/vector", shell=True)


class ExitHandler(server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/quitquitquit":
            return
        print("Exiting.")
        self.send_response(200)
        self.end_headers()

        try:
            outs, errs = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        if outs:
            print(f"{outs=}")
        if errs:
            print(f"{errs=}")
        raise SystemExit()


class ThisServer(server.HTTPServer):
    def service_actions(self):
        proc.poll()
        if proc.returncode is not None:
            raise SystemExit(proc.returncode)


print(f"{ppid=}")

address = ("127.0.0.1", 8000)
server = ThisServer(address, ExitHandler)
server.serve_forever()
