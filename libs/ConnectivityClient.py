import paramiko
import paramiko.ssh_exception
import time
from prometheus_client import Counter, Histogram
from libs.TimeRecorder import TimeRecorder
from libs.PrometheusExporter import CommandTypes, LabelNames

from libs.loggerClass import Logger


class MetricLabels:
    STATUS_CODE = "status_code"
    HOST = "host"
    ENDPOINT = "endpoint"


class ResultStatusCodes:
    SUCCESS = "200"
    FAILURE = "400"


class MetricName:
    SSH_TOT = "ssh_connections_total"
    SSH_CONN_TEST_TOT = "ssh_connectivity_tests_total"
    SSH_CONN_DUR = "ssh_connect_duration_seconds"
    PING_TOT = "connectivity_tests_total"


class MetricDescription:
    SSH_TOT = "Total number of SSH connections"
    SSH_CONN_TEST_TOT = "Total number of SSH connectivity tests"
    SSH_CONN_DUR = "Durations of SSH connections"
    PING_TOT = "Total number of connectivity tests"


class SshClient:
    conn_total_count = Counter(
        MetricName.SSH_TOT,
        MetricDescription.SSH_TOT,
        [MetricLabels.STATUS_CODE, MetricLabels.HOST, LabelNames.COMMAND_LABEL],
    )
    conn_duration = Histogram(
        MetricName.SSH_CONN_DUR,
        MetricDescription.SSH_CONN_DUR,
        [MetricLabels.STATUS_CODE, MetricLabels.HOST, LabelNames.COMMAND_LABEL],
    )
    conn_test_count = Counter(
        MetricName.PING_TOT,
        MetricDescription.PING_TOT,
        [
            MetricLabels.STATUS_CODE,
            MetricLabels.HOST,
            MetricLabels.ENDPOINT,
            LabelNames.COMMAND_LABEL,
        ],
    )

    def __init__(self, host, username, key_path, logger: Logger):
        self.host = host
        self.username = username
        self.client = paramiko.SSHClient()
        policy = paramiko.AutoAddPolicy()
        self.client.set_missing_host_key_policy(policy)
        self.private_key = paramiko.RSAKey.from_private_key_file(key_path)
        self.ping_stat = [0, 0, 0]  # retries, fairure, total
        self.logger = logger

    def log(self, level, message):
        """
        configures behave to print log information greater than min log level

        Args:
            level: (string)
            message: (string)
        """
        if self.logger and level >= self.min_log_level:
            self.logger.log(level, message)

    def execute_command(self, command, ignore_error_output=False):
        """
        Executs provided bashscript on vm and returns the commands response code

        Args:
            command: bashscript (string)
            ignore_error_output: raises exception (string)
        Returns:
            the status of success failures and retries as a list of strings [retries,fairure,total] and the assertionline in case of failures

        Raises:
            Assertion Failed: Failed to test internet connectivity for endpoint, if IP address is in wrong format or unreachable
        """
        try:
            _stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            err_output = stderr.read().decode().strip()
            if err_output and not ignore_error_output:
                raise Exception(err_output)
            return output

        except Exception as e:
            raise RuntimeError(
                f"Failed to execute command '{command}' on server {self.host}: {e}"
            )

    def connect(self):
        """
        establishes connection via ssh by calling the TimeRecorder Class

        Args:
            class
        Returns:
            the status of success failures and retries as a list of strings [retries,fairure,total] and the assertionline in case of failures
        Raises:
            Exception: exceptions.ConnectFailure(msg)
            Assertion Failed: Failed to connect
        """

        def on_success(duration):
            self.conn_total_count.labels(
                ResultStatusCodes.SUCCESS, self.host, CommandTypes.SSH
            ).inc()
            self.conn_duration.labels(
                ResultStatusCodes.SUCCESS, self.host, CommandTypes.SSH
            ).observe(duration)
            # self.assertline=f"SSH connection to server {self.host} established"

        def on_fail(duration, exception):
            self.conn_total_count.labels(
                ResultStatusCodes.FAILURE, self.host, CommandTypes.SSH
            ).inc()
            self.conn_duration.labels(
                ResultStatusCodes.FAILURE, self.host, CommandTypes.SSH
            ).observe(duration)

        # self.assertline=f"SSH connection to server {self.host} failed"
        TimeRecorder.record_time(
            lambda: self.client.connect(
                self.host, username=self.username, pkey=self.private_key
            ),
            on_success=on_success,
            on_fail=on_fail,
        )

    def close_conn(self):
        self.client.close()

    def test_internet_connectivity(self, conn_test, ip="8.8.8.8", tot_ips=1):
        """
        Tests connectivity provided IP address by executing bashscript on vm and tracks failures and retries

        Args:
            conn_test: metric type (string, filter key is command)
            ip: ip address (string)
            tot_ips: total number of ip adresses (int)
        Returns:
            the status of success failures and retries as a list of strings [retries,fairure,total] and the assertionline in case of failures

        Raises:
            Assertion Failed: Failed to test internet connectivity for endpoint, if IP address is in wrong format or unreachable
        """
        self.assertline = ""

        def test_connectivity():
            script = self.create_script(ip, 5, 3)
            output = self.execute_command(script)
            self.ping_stat[2] = tot_ips
            if output != "2":
                self.conn_test_count.labels(
                    ResultStatusCodes.SUCCESS, self.host, ip, conn_test
                ).inc()
                self.assertline = f"Internet connectivity test passed for server {self.host}, Failures: {self.ping_stat[1]}/{self.ping_stat[2]}, Retries: {self.ping_stat[0]}"
            elif output == "2":
                self.ping_stat[1] = self.ping_stat[1] + 1
                self.conn_test_count.labels(
                    ResultStatusCodes.FAILURE, self.host, ip, conn_test
                ).inc()
                self.assertline = f"Failed to test internet connectivity for server {self.host}, Failures: {self.ping_stat[1]}/{self.ping_stat[2]}, Retries: {self.ping_stat[0]}"
            self.logger.log_debug(
                f"ping status [retries,failures,total] {self.ping_stat}"
            )

        test_connectivity()
        return self.ping_stat, self.assertline

    def create_script(self, ip_str, c=1, w=3, c_retry=1, w_retry=3):
        """
        Creates a bash script to ping the provided IP address

        Args:
            ip_str: ip address (string)
            c: count of pings for first try (int)
            w: wait for ping result of first try (int)
            c_retry: count of pings for second try (int)
            w_retry: wait for ping result of second try (int)
        Returns:
            executable bashcript

        Raises:
            Assertion Failed: Failed to test internet connectivity for endpoint, if IP address is in wrong format or unreachable
        """
        self.logger.log_debug("create script ip string{ip_str}")
        script_content = f"""
            #!/bin/bash

            myping() {{
                if ping -c{c} -w{w} $1 >/dev/null 2>&1; then echo return 0; fi
                sleep 1
                if ping -c{c_retry} -w{w_retry} $1 >/dev/null 2>&1; then return 1; fi
                return 2
            }}

            ips=({ip_str})
            for ip in "${{ips[@]}}"; do
                myping $ip
                result=$?
                echo $result
            done
            """
        return script_content

    def install_ping(self):
        """
        installs ping on vm

        Args:
            class
        Returns:
            response from command execution
        Raises:
            Exception: exceptions.ConnectFailure(msg)
            Assertion Failed: Failed to connect
        """

        command = "sudo apt-get update -y && sudo apt-get install -y iputils-ping"
        response = self.execute_command(command, True)
        return response

    def print_working_directory(self):
        """
        prints current working dir on vm

        Args:
            class
        Returns:
            prints current working dir
        Raises:
            Exception:
        """
        directory = self.execute_command("pwd")
        self.logger.log_info(
            f"Current working directory on server {self.host}: {directory}"
        )

    def check_ssh_ready(self) -> bool:
        """Check if ssh is ready on a provisioned server.

        Returns:
            True if server is ready to respond to ssh connection, else False.
        """
        try:
            self.connect()
            self.close_conn()
            return True
        except (
            paramiko.ssh_exception.NoValidConnectionsError,
            paramiko.ssh_exception.SSHException,
        ):
            return False
        except Exception as e:
            self.logger.log_error(f"Error occurred: {e}")
            return False

    def check_server_readiness(self, attempts: int, timeout: int = 10) -> bool:
        """Check if server is ready for ssh connection defined amount of times.

        Args:
            attempts: Number of attempts to check server readiness.
            timeout: Time to wait after each attempt.

        Returns:
            True if server is ready to respond to ssh connection, else False.
        """
        for i in range(attempts):
            if self.check_ssh_ready():
                return True
            else:
                self.logger.log_info(
                    f"Server unavailable, retrying in {timeout} seconds."
                )
                time.sleep(timeout)
        return False
