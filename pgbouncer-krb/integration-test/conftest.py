"""Show test.py's log as it runs, since the suite takes about 90 seconds.

Any --log-cli-* option passed on the command line takes precedence.
"""


def pytest_configure(config):
    if config.getoption("log_cli_level") is None:
        config.option.log_cli_level = "INFO"
    if config.getoption("log_cli_format") is None:
        config.option.log_cli_format = "%(asctime)s %(message)s"
    if config.getoption("log_cli_date_format") is None:
        # With the zone, since the pgbouncer and klist lines it logs are in UTC.
        config.option.log_cli_date_format = "%H:%M:%S %Z"
