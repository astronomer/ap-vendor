#!/usr/bin/env python3
"""Launch vector in a subprocess and watch for signals from airflow.

There are two signals from airflow that are handled:
* /var/log/sidecar-log-consumer/heartbeat is an optional file that shows a unix timestamp of the last heartbeat.
* /var/log/sidecar-log-consumer/finished signals that airflow is done and this script should also finish up.

Other behaviors of this script:
* If the "heartbeat" file doesn't exist, this script waits for it to show up.
* If the "heartbeat" file never shows up, this script will only exit when the "finished" file shows up or when
  it receives a process signal to exit.
* If the "heartbeat" file disappears or becomes empty, the last known heartbeat is used.
* If the "finished" file is seen, the script will ask vector to quit and then exit.
* If the script is killed, vector is terminated.

"""

import signal
import subprocess
import sys
import time
from pathlib import Path


def signal_handler(sig, _):
    print(f"Received signal {sig}", flush=True)
    if handler:
        handler.quit_proc()
    sys.exit(0)


class VectorHandler:
    airflow_finished_file = Path("/var/log/sidecar-log-consumer/finished")
    airflow_heartbeat_file = Path("/var/log/sidecar-log-consumer/heartbeat")
    airflow_heartbeat_max_age = 120  # seconds
    airflow_heartbeat_timestamp = None

    def __init__(self):
        self.vector = subprocess.Popen(["/usr/local/bin/vector"], shell=False)

    def quit_proc(self):
        """Ask vector to quit nicely, and kill it after 60 if it does not quit."""
        try:
            print("Terminating.", flush=True)
            self.vector.terminate()
            self.vector.wait(timeout=60)
        except subprocess.TimeoutExpired:
            print("Termination timed out. Killing.", flush=True)
            self.vector.kill()

    def check_heartbeat(self):
        if self.airflow_heartbeat_file.exists():
            # Sometimes the file contents are empty due to a race condition, so we only update
            # airflow_heartbeat_timestamp if the file contents can be converted to a float.
            if airflow_heartbeat_timestamp := float(self.airflow_heartbeat_file.read_text()):
                self.airflow_heartbeat_timestamp = airflow_heartbeat_timestamp

        if self.airflow_heartbeat_timestamp:
            self.airflow_heartbeat_age = time.time() - self.airflow_heartbeat_timestamp
            if self.airflow_heartbeat_age > self.airflow_heartbeat_max_age / 2:
                print(
                    f"WARNING: Heartbeat has not been sent for {self.airflow_heartbeat_age:0.1f} seconds",
                    flush=True,
                )
            if self.airflow_heartbeat_age > self.airflow_heartbeat_max_age:
                raise SystemExit("ERROR: Heartbeat is gone. Exiting.")

    def run(self):
        """Run a loop that handles signals from the Airflow container and monitors the proc. Exit when needed."""
        while not self.airflow_finished_file.exists():
            self.vector.poll()
            if self.vector.returncode is not None:
                print("Vector has quit. Exiting.")
                raise SystemExit(self.vector.returncode)
            self.check_heartbeat()
            time.sleep(5)

        print("Airflow has exited.")


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

handler = VectorHandler()
try:
    handler.run()
finally:
    handler.quit_proc()
