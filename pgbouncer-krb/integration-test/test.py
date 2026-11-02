"""End-to-end Kerberos test for the ap-pgbouncer-krb image.

docker-compose.yaml brings up a KDC, a Postgres that only accepts GSSAPI for the
`houston` role, and pgbouncers from the image under test, locked down the way the
platform chart runs them:

  - pgbouncer-gss: server_gssauth_negotiate on
  - pgbouncer-openshift: the same, as an arbitrary UID with GID 0
  - pgbouncer-nogss: negotiation off

Clients log in to pgbouncer with a password, as app_md5 (md5) or app_scram (SCRAM);
pgbouncer always logs in to Postgres as houston. Build the image first, then run:

    ASTRO_IMAGE_NAME=ap-pgbouncer-krb uv run pytest -v pgbouncer-krb/integration-test/test.py
"""

import os
import time
import uuid
from pathlib import Path

import pytest
from python_on_whales import DockerClient, DockerException

ASTRO_IMAGE_NAME = os.getenv("ASTRO_IMAGE_NAME", "ap-pgbouncer-krb")
ASTRO_IMAGE_TAG = os.getenv("ASTRO_IMAGE_TAG", os.getenv("CIRCLE_SHA1", "latest"))

# The password of both users in userlist.txt.
CLIENT_PASSWORD = "not-a-secret"  # noqa: S105
# Must match the maxlife in kdc-entrypoint.sh and the clockskew in krb5.conf.
TICKET_LIFETIME_SECONDS = 60
CLOCK_SKEW_SECONDS = 5

# Run on the Postgres side of the connection pgbouncer opened, so it reports how
# pgbouncer authenticated, not how the test client did.
GSS_STATUS_QUERY = "select gss_authenticated, principal, encrypted from pg_stat_gssapi where pid = pg_backend_pid()"
# GSSAPI-authenticated as houston, and not encrypted: the patch does auth only.
GSS_AUTHENTICATED = "t|houston@KRB.TEST|f"


@pytest.fixture(scope="module")
def stack():
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("PGBOUNCER_IMAGE", f"{ASTRO_IMAGE_NAME}:{ASTRO_IMAGE_TAG}")
        docker = DockerClient(
            compose_files=[Path(__file__).parent / "docker-compose.yaml"],
            compose_project_name=f"pgbouncer-krb-it-{uuid.uuid4().hex[:8]}",
        )
        try:
            try:
                docker.compose.up(detach=True, wait=True, quiet=True)
            except DockerException:
                # CI can't inspect the containers afterwards, so show why the stack didn't come up.
                print(docker.compose.logs())
                raise
            yield docker
        finally:
            docker.compose.down(volumes=True, quiet=True)


def query_through(stack: DockerClient, pgbouncer: str, user: str = "app_scram", password: str = CLIENT_PASSWORD) -> str:
    """Run GSS_STATUS_QUERY through the given pgbouncer service, using psql from the Postgres container."""
    return stack.compose.execute(
        "postgres",
        ["psql", f"host={pgbouncer} port=6432 dbname=gssdb user={user} connect_timeout=15", "-At", "-c", GSS_STATUS_QUERY],
        envs={"PGPASSWORD": password},
        tty=False,
    ).strip()


@pytest.mark.parametrize("pgbouncer", ["pgbouncer-gss", "pgbouncer-openshift"])
def test_gssapi_login_through_pgbouncer(stack, pgbouncer):
    """pgbouncer's server connection must be GSSAPI-authenticated as houston, also when OpenShift assigns the UID."""
    assert query_through(stack, pgbouncer) == GSS_AUTHENTICATED, stack.compose.logs([pgbouncer, "postgres", "kdc"])


@pytest.mark.parametrize("user", ["app_md5", "app_scram"])
def test_client_password_login(stack, user):
    """Clients log in to pgbouncer with md5 or SCRAM, while pgbouncer still logs in to Postgres with GSSAPI."""
    assert query_through(stack, "pgbouncer-gss", user=user) == GSS_AUTHENTICATED, stack.compose.logs("pgbouncer-gss")


@pytest.mark.parametrize(
    ("user", "error"),
    [("app_md5", "password authentication failed"), ("app_scram", "SASL authentication failed")],
)
def test_client_wrong_password_is_rejected(stack, user, error):
    """A wrong password is refused, and the error shows which mechanism pgbouncer used (SASL means SCRAM)."""
    with pytest.raises(DockerException, match=error):
        query_through(stack, "pgbouncer-gss", user=user, password="wrong-password")  # noqa: S106


def test_login_refused_without_gssapi_negotiation(stack):
    """With negotiation off, pgbouncer must refuse Postgres's GSSAPI request rather than log in another way."""
    with pytest.raises(DockerException):
        query_through(stack, "pgbouncer-nogss")
    logs = stack.compose.logs("pgbouncer-nogss")
    assert "failed to answer authreq" in logs, logs


def test_gssapi_login_after_tickets_expire(stack):
    """pgbouncer outlives its Kerberos tickets; once they expire it must get new ones from its keytab."""
    assert query_through(stack, "pgbouncer-gss") == GSS_AUTHENTICATED
    tickets_before = stack.compose.execute("pgbouncer-gss", ["klist"], tty=False)
    # Long before this ends, server_idle_timeout has closed the server connection, so the
    # next query has to authenticate a new one.
    time.sleep(TICKET_LIFETIME_SECONDS + CLOCK_SKEW_SECONDS + 10)
    assert query_through(stack, "pgbouncer-gss") == GSS_AUTHENTICATED, stack.compose.logs(["pgbouncer-gss", "postgres", "kdc"])
    tickets_after = stack.compose.execute("pgbouncer-gss", ["klist"], tty=False)
    assert tickets_after != tickets_before, f"pgbouncer kept its first tickets, so expiry was never exercised:\n{tickets_after}"
