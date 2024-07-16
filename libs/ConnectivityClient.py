
import paramiko
import paramiko.ssh_exception
import time
from prometheus_client import Counter, Histogram
from libs.TimeRecorder import TimeRecorder
from libs.PrometheusExporter import CommandTypes, LabelNames

from libs.loggerClass import Logger

import os
import time
import json
from decimal import Decimal

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
            self.logger.log_info(
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
    
########################## iperf
    def transfer_wait_script(self, float_ip, pno, testname):
        """
            transfers temporary local wait script to the target host (and excecutes it?)
            Args:
                float_ip: floating ip
                pno: portnumber
                testname: testname for namespace
            Returns:
                
            Raises:
                Exception:
                    if file not found
        """
        # scp_command = f"scp -o UserKnownHostsFile=~/.ssh/known_hosts.{testname} -o PasswordAuthentication=no " \
        #             f"-o StrictHostKeyChecking=no -i {DATADIR}/{KEYPAIRS[1]} -P {pno} -p {testname}-wait {DEFLTUSER}@{float_ip}:"
        # subprocess.run(scp_command, shell=True, stdout=subprocess.DEVNULL)

        sftp = self.client.open_sftp()
        directory = self.execute_command("pwd")
        print(f"open sftp pwd {directory}")
        sftp.put(f"{testname}-wait",os.path.join("/home/ubuntu",f"{testname}-wait"))
        directory = self.execute_command("pwd")
        peek=self.execute_command("ls -la")        
        print(f"peek: {peek}")
        print("File transfer completed successfully.")
        if sftp:
                sftp.close()

    def iperf3_sub(self, source_ip, target_ip, float_ip, pno, testname):
        # iperf_command = f"echo hello world"
        # print("iperf3 sub")
        # iperf_command = f"ssh -o UserKnownHostsFile=~/.ssh/known_hosts.{testname} -o PasswordAuthentication=no " \
        #         f"-o StrictHostKeyChecking=no -i {self.private_key} -p {pno} {self.username}@{float_ip} " \
        #         f"./{testname}-wait iperf3; iperf3 -t5 -J -c {target_ip} &"
        target_ip="213.131.230.87"
        pno="22"
        iperf_command = f"ssh -o UserKnownHostsFile=~/.ssh/known_hosts.{testname} -o PasswordAuthentication=no " \
                        f"-o StrictHostKeyChecking=no -p {pno} {self.username}@{float_ip} " \
                        f"./{testname}-wait iperf3; iperf3 -t5 -J -c {target_ip} &"
        try:
            #IPJSON = subprocess.check_output(iperf_command, shell=True)
            IPJSON = self.execute_command(iperf_command)
            self.logger.log_info(f"iperf json {IPJSON}")
        except:
            self.logger.log_error(f"Iperf json retry")
            time.sleep(16)

        # except subprocess.CalledProcessError:
        #     print(" retry ", end='')
        #     time.sleep(16)
    def parse_and_log_results(self,IPJSON, source_ip, target_ip, vm):
        print("parse")
        BOLD = '\033[1m'
        NORM = '\033[0m'
        BANDWIDTH = []
        self.logger.log_info(f"{IPJSON}\n")
    
        ipjson_dict = json.loads(IPJSON)
        SENDBW = int(Decimal(ipjson_dict['end']['sum_sent']['bits_per_second']) / 1048576)
        RECVBW = int(Decimal(ipjson_dict['end']['sum_received']['bits_per_second']) / 1048576)
        HUTIL = f"{ipjson_dict['end']['cpu_utilization_percent']['host_total']:.1f}%"
        RUTIL = f"{ipjson_dict['end']['cpu_utilization_percent']['remote_total']:.1f}%"
    
        print(f" {source_ip} <-> {target_ip}: {BOLD}{SENDBW} Mbps {RECVBW} Mbps {HUTIL} {RUTIL}{NORM}")
        self.logger.log_info(f"IPerf3: {source_ip}-{target_ip}: {SENDBW} Mbps {RECVBW} Mbps {HUTIL} {RUTIL}\n")
    
        BANDWIDTH.extend([SENDBW, RECVBW])
        SBW = float(Decimal(SENDBW) / 1000)
        RBW = float(Decimal(RECVBW) / 1000)

        self.logger.log_info(f"Bandwith: {BANDWIDTH} SBW: {SBW} RBW: {RBW}\n")

    def get_last_non_empty_line(self,text):
        ''' 
        get the last non-empty line
        '''
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return non_empty_lines[-1] if non_empty_lines else None

    def extract_pno(self, text):
        '''
        extract pno from red
        '''
        if 'tcp,' in text:
            start_index = text.index('tcp,') + len('tcp,')
            end_index = text.find(',', start_index)
            if end_index == -1:
                return text[start_index:]
            return text[start_index:end_index]
        return None

        
    def log_to_file(logfile, message):
        '''
        log to a file
        '''
        with open(logfile, 'a') as f:
            f.write(message + '\n')

    def run_iperf_test(self, testname, ips, network_quantity: int=3, redirs=["tcp,8080, value1", "tcp,9090, value1"], avail_zones=2):
        print(f"testname: {testname},  ips: { ips}, network_quantity: {network_quantity}") 
        self.print_working_directory()
        # script_path=self.create_wait_script("iperf3",testname)
        # print(f"scriptpath {script_path}")
        NOVMS = len( ips)
        floating_ips = ["213.131.230.87", "213.131.230.10"]
        red = redirs[avail_zones - 1]
        red = self.get_last_non_empty_line(red)
        pno = self.extract_pno(red)
        print(f"Redirect: {redirs[0]} red: {red} pno: {pno}")
        print("...")
        print(f"type(network_quantity): {type(network_quantity)}")
        print("...")
        for vm in range(network_quantity):
            target_ip =  ips[vm] if  ips[vm] else  ips[vm + network_quantity]
            source_ip =  ips[vm + NOVMS - network_quantity] if  ips[vm + NOVMS - network_quantity] else  ips[vm + NOVMS - 2 * network_quantity]
            print(f"target_ip: {target_ip} source_ip: {source_ip}")

            if not source_ip or not target_ip or source_ip == target_ip:
                error_message = f"#ERROR: Skip test {source_ip} <-> {target_ip}"
                print(error_message)
                self.logger.log_info(f"IPerf3: {source_ip}-{target_ip}: skipped")


            float_ip = floating_ips[vm % avail_zones]
            # # Perform operations as in the shell script
            # # SSH and SCP operations are placeholders here
            # scp_command = f"scp -P {pno} file {float_ip}"
            # ssh_command = f"ssh -p {pno} {float_ip} iperf3 -t5 -J -c {target_ip}"

            print(f"float_ip {float_ip}")
            print("...")            
            self.transfer_wait_script(float_ip, pno, testname)
            # self.logger.log_info(f"ssh -o \"UserKnownHostsFile=~/.ssh/known_hosts.{testname}\" -o \"PasswordAuthentication=no\" "
            #                 f"-o \"StrictHostKeyChecking=no\" -i {self.private_key} -p {pno} {self.username}@{float_ip} "
            #                 f"iperf3 -t5 -J -c {target_ip}\n")
    
            IPJSON = self.iperf3_sub(source_ip, target_ip, float_ip, pno, testname)

            print(f"ipjson {IPJSON}")

            if IPJSON:
                self.parse_and_log_results(IPJSON, source_ip, target_ip, vm)