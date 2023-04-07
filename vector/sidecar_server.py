#!/usr/bin/env python3
"""Launch vector in a subprocess and handle web signaling for the sidecar. This now requires the airflow container
to open up 127.0.0.1:13579 as a way to show that it is alive.
"""
import time
import os
import subprocess
from http import server
import socket

ppid = os.getppid()

proc = subprocess.Popen("/usr/local/bin/vector", shell=True)


def quit_proc():
    try:
        print("Terminating.")
        proc.terminate()
        proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        print("Termination timed out. Killing.")
        proc.kill()


class AirflowLiveness:
    """
    Implementation of a minimal liveness status between containers. The primary container will bind to a 127.0.0.1
    port, but not open it. Sidecar containers can attempt to bind to that port in order to see if the primary
    container is still alive. This allows us to check the status of the other container without needing more
    complicated heartbeat logic. One notable behavior of this method is that the port will not show up as open in
    netstat, /proc/net/tcp, lsof -i, ss, or other tools. This is because the port is not open, it is just reserved
    for use.

    This is only a fallback in case the primary container is brutally killed and cannot not POST /quitquitquit.
    """

    port = 13579
    last_seen = time.time()
    max_last_seen = 180  # seconds

    def is_socket_bound(self):
        """Check if self.port is bound."""

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.bind(("127.0.0.1", self.port))
            print(
                f"Have not seen liveness port in {time.time() - self.last_seen:0.3f} seconds"
            )
            return False
        except socket.error:
            return True
        finally:
            sock.close()

    def alive_handler(self):
        """Look for the binding of self.port and watch it until it goes away."""

        if self.is_socket_bound():
            self.last_seen = time.time()

        if time.time() - self.last_seen > self.max_last_seen:
            return False

        return True

    def is_airflow_alive(self):
        return self.alive_handler()


class MessageHandler(server.BaseHTTPRequestHandler):
    """Listen for a POST to /quitquitquit to signal that the sidecar should exit. Also keep an eye on the liveness
    port to see if the primary container has been brutally killed."""

    def do_POST(self):
        if self.path != "/quitquitquit":
            return

        self.send_response(200)
        self.end_headers()

        quit_proc()
        raise SystemExit()


class MessageServer(server.HTTPServer):
    af_heartbeat = AirflowLiveness()

    def service_actions(self):
        proc.poll()
        if proc.returncode is not None:
            raise SystemExit(proc.returncode)

        if not self.af_heartbeat.is_airflow_alive():
            print(f"{self.af_heartbeat.is_airflow_alive()=}")
            quit_proc()
            raise SystemExit(proc.returncode)


print(f"{ppid=}")

address = ("127.0.0.1", 8000)
server = MessageServer(address, MessageHandler)
server.serve_forever()
