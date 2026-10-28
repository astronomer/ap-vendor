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
* On SIGTERM/SIGINT in a worker pod, vector is kept running until the worker's task log server port closes. See
  wait_for_worker_drain.

"""

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

# Kubernetes delivers SIGTERM to every container in a pod at once, but the worker container finishes its running
# task before exiting. Quitting vector immediately would drop everything the task logs after the signal.
# The worker serves task logs on this port, over the pod's shared network namespace, for as long as it is alive,
# and the port closes when the worker has finished its current task.
WORKER_LOG_SERVER_HOST = "127.0.0.1"
WORKER_LOG_SERVER_PORT = 8793
# Time for vector to read the last lines written before the worker exited, and to flush them to the sink.
WORKER_DRAIN_SETTLE_SECONDS = 5

shutting_down = False


def worker_log_server_is_up():
    try:
        with socket.create_connection((WORKER_LOG_SERVER_HOST, WORKER_LOG_SERVER_PORT), timeout=2):
            return True
    except OSError:
        return False


def wait_for_worker_drain():
    """Block until the worker container has finished its current task, so vector keeps shipping its logs.

    There is no timeout of our own: the kubelet SIGKILLs the pod at terminationGracePeriodSeconds regardless.
    Only applies to the worker component. Returns immediately if the log server is not listening, so a worker
    that is already gone, or one that never exposed the port, does not delay shutdown.
    """
    if os.environ.get("COMPONENT") != "worker" or not worker_log_server_is_up():
        return

    print(
        f"Waiting for the worker log server on port {WORKER_LOG_SERVER_PORT} to close before stopping vector.",
        flush=True,
    )
    while worker_log_server_is_up():
        time.sleep(1)

    print(f"Worker has finished. Letting vector flush for {WORKER_DRAIN_SETTLE_SECONDS}s.", flush=True)
    time.sleep(WORKER_DRAIN_SETTLE_SECONDS)


def signal_handler(sig, _):
    global shutting_down
    print(f"Received signal {sig}", flush=True)
    if shutting_down:
        return
    shutting_down = True
    wait_for_worker_drain()
    if handler:
        handler.quit_proc()
    sys.exit(0)


class VectorHandler:
    airflow_finished_file = Path("/var/log/sidecar-log-consumer/finished")
    airflow_heartbeat_file = Path("/var/log/sidecar-log-consumer/heartbeat")
    airflow_heartbeat_max_age = 120  # seconds
    airflow_heartbeat_timestamp = None

    def __init__(self):
        self.vector = subprocess.Popen(["/usr/bin/vector"], shell=False)

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
            raw_value = self.airflow_heartbeat_file.read_text().strip()
            if raw_value:
                airflow_heartbeat_timestamp = float(raw_value)
                self.airflow_heartbeat_timestamp = airflow_heartbeat_timestamp
            else:
                print("WARNING: Heartbeat file exists but is empty", flush=True)

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
