#!/usr/bin/env python3
"""Launch vector in a subprocess and listen for POST /quitquitquit. Also keep an eye on
/var/log/sidecar-log-consumer/heartbeat, which may exist and will have a unix timestamp
representing the last heartbeat from the airflow container.
"""
import time
import os
import subprocess
from http import server
from pathlib import Path

ppid = os.getppid()

proc = subprocess.Popen("/usr/local/bin/vector", shell=True)


def quit_proc():
    try:
        print("Terminating.", flush=True)
        proc.terminate()
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        print("Termination timed out. Killing.", flush=True)
        proc.kill()


class MessageHandler(server.BaseHTTPRequestHandler):
    """Listen for a POST to /quitquitquit to signal that the sidecar should exit. Also keep
    an eye on the heartbeat file to see if the primary container has been brutally killed.
    """

    def do_POST(self):
        if self.path != "/quitquitquit":
            return

        self.send_response(200)
        self.end_headers()

        quit_proc()
        raise SystemExit()


class MessageServer(server.HTTPServer):
    heartbeat_file = Path("/var/log/sidecar-log-consumer/heartbeat")
    heartbeat_max_age = 180  # seconds

    def service_actions(self):
        proc.poll()
        if proc.returncode is not None:
            raise SystemExit(proc.returncode)

        if self.heartbeat_file.exists():
            age = time.time() - float(self.heartbeat_file.read_text())
            if age > self.heartbeat_max_age / 2:
                print(
                    f"WARNING: Heartbeat has not been sent for {age:0.1f} seconds",
                    flush=True,
                )
            if age > self.heartbeat_max_age:
                raise SystemExit("ERROR: Heartbeat is gone. Exiting.", flush=True)


print(f"{ppid=}", flush=True)

address = ("127.0.0.1", 8000)
server = MessageServer(address, MessageHandler)
server.serve_forever()
