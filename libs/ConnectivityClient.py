
import paramiko
import paramiko.ssh_exception
import time
from prometheus_client import Counter, Histogram, Gauge
from libs.TimeRecorder import TimeRecorder
from libs.PrometheusExporter import CommandTypes, LabelNames, LabelValues

from libs.loggerClass import Logger

import os
import time
import json
from decimal import Decimal

class MetricLabels:
    STATUS_CODE = "status_code"
    HOST = "host"
    ENDPOINT = "endpoint"
    SENDER_IP = "sender_ip"
    SENDER_NAME = "sender_name"
    RECEIVER_IP = "receiver_ip"
    RECEIVER_NAME = "receiver_name"
 #   RESULT = "testresult"


class ResultStatusCodes:
    SUCCESS = "200"
    FAILURE = "400"


class MetricName:
    SSH_TOT = "ssh_connections_total"
    SSH_CONN_TEST_TOT = "ssh_connectivity_tests_total"
    SSH_CONN_DUR = "ssh_connect_duration_seconds"
    PING_TOT = "connectivity_tests_total"
    IPERF3_BANDWIDTH_SENDER = "iperf3_bandwidth_sender_gigabits"
    IPERF3_BANDWIDTH_RECEIVER = "iperf3_bandwidth_receiver_gigabits"
    IPERF3_CPU_SENDER = "iperf3_cpu_utilization_sender_percentage"
    IPERF3_CPU_RECEIVER = "iperf3_cpu_utilization_receiver_percentage"


class MetricDescription:
    SSH_TOT = "Total number of SSH connections"
    SSH_CONN_TEST_TOT = "Total number of SSH connectivity tests"
    SSH_CONN_DUR = "Durations of SSH connections"
    PING_TOT = "Total number of connectivity tests"
    IPERF3_BANDWIDTH_SENDER = "iperf3 benchmark bandwidth at sender side"
    IPERF3_BANDWIDTH_RECEIVER = "iperf3 benchmark bandwidth at receiver side"
    IPERF3_CPU_SENDER = "CPU utilization of sender during iperf3 run"
    IPERF3_CPU_RECEIVER = "CPU utilization of receiver during iperf3 run"


class SshClient:

    """
    Connection metrics
    """

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

    """
    Iperf3 metrics
    """

    iperf_common_labels = [
        MetricLabels.SENDER_IP,
        MetricLabels.SENDER_NAME,
        MetricLabels.RECEIVER_IP,
        MetricLabels.RECEIVER_NAME,
        LabelNames.COMMAND_LABEL,
    ]

    iperf3_bandwidth_sender = Gauge(
        MetricName.IPERF3_BANDWIDTH_SENDER,
        MetricDescription.IPERF3_BANDWIDTH_SENDER,
        labelnames=iperf_common_labels,
    )

    iperf3_bandwidth_receiver = Gauge(
        MetricName.IPERF3_BANDWIDTH_RECEIVER,
        MetricDescription.IPERF3_BANDWIDTH_RECEIVER,
        labelnames=iperf_common_labels,
    )

    iperf3_cpu_sender = Gauge(
        MetricName.IPERF3_CPU_SENDER,
        MetricDescription.IPERF3_CPU_SENDER,
        labelnames=iperf_common_labels,
    )

    iperf3_cpu_receiver = Gauge(
        MetricName.IPERF3_CPU_RECEIVER,
        MetricDescription.IPERF3_CPU_RECEIVER,
        labelnames=iperf_common_labels,
    )

    def __init__(self, host, username, key_path, logger: Logger, port=22):
        self.host = host
        self.port = port
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
                self.host, port=self.port, username=self.username, pkey=self.private_key
            ),
            on_success=on_success,
            on_fail=on_fail,
        )

    def close_conn(self):
        self.client.close()
        self.logger.log_info("ssh connection closed")

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
                self.assertline = f"Failed to test connectivity for server {self.host}, Failures: {self.ping_stat[1]}/{self.ping_stat[2]}, Retries: {self.ping_stat[0]}"
            self.logger.log_info(
                f"ping status {ip} [retries,failures,total] {self.ping_stat}"
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
    
    def transfer_script(self, scriptname):
        """
            transfers temporary local script to the connected host via sftp, not used for now
            Args:
                testname: testname for namespace
            Returns:
                
            Raises:
                Exception:
                    if file not found
        """

        sftp = self.client.open_sftp()
        host = self.execute_command("hostname -I")
        directory = self.execute_command("pwd")
        sftp.put(scriptname,os.path.join(directory,scriptname))
        peek=self.execute_command("ls -la")        
        self.logger.log_debug(f"peek: {peek}")
        self.logger.log_info(f"{scriptname} transfer completed successfully to {host}: {directory}.")
        if sftp:
            sftp.close()

    def get_iperf3(self, target_ip, retries = 5):
        """
            performs an iperf3-client request on the server addressed by the target ip
            Args:
                target_ip: (string) network ip address of the iperf3 server, usually the jh 
                retries: (int) number of retries in case of failure
            Returns:
                iperf_json: (json) iperf response as json
            Raises:
                checks if command is succesfully executed
                and whether the iperf response contains any errors
        """
        iperf_command = f"iperf3 -t5 -J -c {target_ip} | jq"
        iperf_json = None
        substring = "error"
        error = False
        for i in range(1, retries):
            try:
                iperf_json = self.execute_command(iperf_command)
                self.logger.log_info(f"received Iperf response as json")
                if iperf_json.find(substring) != -1:
                    error= True
            except:
                error = True
                self.logger.log_error(f"Iperf request failed retry {i}")
            if iperf_json != None and error == False:
                self.logger.log_info(f"Iperf without any errors")
                break
            self.logger.log_error(f"Iperf retry {i}")
            time.sleep(10)    
        return iperf_json


    def parse_iperf_result(self,iperf_json, source_ip, source_name, target_ip, target_name):
        '''
            Parses the result from iperf3
            Args:
                iperf_json: response from iperf formatted as json (string)
            Returns:
                Bandwith
        '''
        bold = '\033[1m'
        norm = '\033[0m'
        bandwidth = []
    
        iperf_json_dict = json.loads(iperf_json)
        print(iperf_json_dict)
        
        send_bw_bits = int(Decimal(iperf_json_dict['end']['sum_sent']['bits_per_second']))
        recv_bw_bits = int(Decimal(iperf_json_dict['end']['sum_received']['bits_per_second']))
        sendBW = send_bw_bits / 1048576
        recvBW = recv_bw_bits / 1048576
        host_util = iperf_json_dict['end']['cpu_utilization_percent']['host_total']
        remote_util = iperf_json_dict['end']['cpu_utilization_percent']['remote_total']
    
        self.logger.log_info(f"IPerf3: {source_ip}-{target_ip}: sendbw: {sendBW} Mbps receivebw: {recvBW} Mbps cpuhost {host_util:.1f}% cpuremote {remote_util:.1f}%\n")

    
    
        bandwidth.extend([sendBW, recvBW])
        sBW = float(Decimal(sendBW) / 1000)
        rBW = float(Decimal(recvBW) / 1000)

        iperf_common_label_values = [
            source_ip,
            source_name,
            target_ip,
            target_name,
            LabelValues.COMMAND_VALUE_IPERF3,
        ]

        self.iperf3_bandwidth_sender.labels(
            *iperf_common_label_values,
        ).set(sBW)

        self.iperf3_bandwidth_receiver.labels(
            *iperf_common_label_values,
        ).set(rBW)

        self.iperf3_cpu_sender.labels(
            *iperf_common_label_values,
        ).set(host_util)

        self.iperf3_cpu_receiver.labels(
            *iperf_common_label_values,
        ).set(remote_util)

        self.logger.log_info(f"Bandwith: {bandwidth} SBW: {sBW} RBW: {rBW}\n")
        return sBW,rBW

    
            
    def run_iperf_test(self, conn_test, testname ,server_fip, target_ip, target_name, source_ip, source_name):
        '''
            iterates through jh (one per network) picks the last vm accessable through jh and sets it as target
            the jh is set as source
        '''
        #self.transfer_script(f"{testname}-wait")
        iperf_json = self.get_iperf3(target_ip)
        if iperf_json:
            self.parse_iperf_result(iperf_json, source_ip, source_name, target_ip, target_name)
            self.conn_test_count.labels(
                ResultStatusCodes.SUCCESS, self.host, target_ip, conn_test
            ).inc()
        else:
            self.conn_test_count.labels(
                ResultStatusCodes.FAILURE, self.host, target_ip, conn_test
            ).inc()
            return f"no iperf-response json"