import paramiko
from prometheus_client import Counter, Histogram
from libs.TimeRecorder import TimeRecorder
from libs.PrometheusExporter import CommandTypes, LabelNames


class SshClientMetricLabels:
    STATUS_CODE = 'status_code'
    HOST = 'host'
    ENDPOINT = 'endpoint'


class SshClientResultStatusCodes:
    SUCCESS = '200'
    FAILURE = '400'


class SshClient:
    connection_count = Counter('ssh_connections_total', 'Total number of SSH connections',
                               [SshClientMetricLabels.STATUS_CODE, SshClientMetricLabels.HOST,
                                LabelNames.COMMAND_LABEL])
    connectivity_test_count = Counter('ssh_connectivity_tests_total', 'Total number of SSH connectivity tests',
                                      [SshClientMetricLabels.STATUS_CODE, SshClientMetricLabels.HOST,
                                       SshClientMetricLabels.ENDPOINT, LabelNames.COMMAND_LABEL])
    connect_duration = Histogram('ssh_connect_duration_seconds', 'Durations of SSH connections',
                                 [SshClientMetricLabels.STATUS_CODE, SshClientMetricLabels.HOST,
                                  LabelNames.COMMAND_LABEL])

    def __init__(self, host, username, key_path):
        self.host = host
        self.username = username
        self.client = paramiko.SSHClient()
        policy = paramiko.AutoAddPolicy()
        self.client.set_missing_host_key_policy(policy)
        self.private_key = paramiko.RSAKey.from_private_key_file(key_path)

    def log(self, level, message):
        if self.logger and level >= self.min_log_level:
            self.logger.log(level, message)

    def execute_command(self, command, ignore_error_output=False):
        try:
            _stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            err_output = stderr.read().decode().strip()

            if err_output and not ignore_error_output:
                raise Exception(err_output)

            return output

        except Exception as e:
            raise RuntimeError(f"Failed to execute command '{command}' on server {self.host}: {e}")

    def connect(self):
        print("connect")
        def on_success(duration):

            self.connection_count.labels(SshClientResultStatusCodes.SUCCESS,
                                         self.host, CommandTypes.SSH).inc()
            self.connect_duration.labels(SshClientResultStatusCodes.SUCCESS,
                                         self.host, CommandTypes.SSH).observe(duration)

        def on_fail(duration, exception):
            self.connection_count.labels(SshClientResultStatusCodes.FAILURE, self.host,
                                         CommandTypes.SSH).inc()
            self.connect_duration.labels(SshClientResultStatusCodes.FAILURE, self.host,
                                         CommandTypes.SSH).observe(
                duration)
            
        TimeRecorder.record_time(
            lambda: self.client.connect(self.host, username=self.username, pkey=self.private_key),
            on_success=on_success,
            on_fail=on_fail
        )
        print(TimeRecorder)

    def close_conn(self):
        self.client.close()

    def test_internet_connectivity(self, domain='google.com'):
        def test_connectivity():
            script = self.create_script([domain],5,1,0,0)
            output = self.execute_command(script)
            #output = self.execute_command(f"ping -c 5 {domain}")
            print(f"domain {domain}")
            print(output)
            # Check for packet loss in the output
            packet_loss_percentage = self.parse_packet_loss(output)
            print(f"packet_loss_percentage {packet_loss_percentage}")
            if packet_loss_percentage == 100:
                raise Exception(f"100% packet loss detected to {domain}")

        def on_success(duration):
            self.connectivity_test_count.labels(SshClientResultStatusCodes.SUCCESS, self.host, domain,
                                                CommandTypes.SSH).inc()
            print(f"Internet connectivity test passed for server {self.host}, Domain: {domain}")

        def on_fail(duration, exception):
            self.connectivity_test_count.labels(SshClientResultStatusCodes.FAILURE, self.host, domain,
                                                CommandTypes.SSH).inc()
            print(f"Failed to test internet connectivity for server {self.host}, Domain: {domain}\nError: {exception}")

        TimeRecorder.record_time(
            test_connectivity,
            on_success=on_success,
            on_fail=on_fail
        )


    def create_script(self,ips,c=1,w=1,c_retry=1,w_retry=3):
        total= len(ips)
        ip_list_str = ' '.join(ips)
        print(f"SSH Connectivity Check ... ({ip_list_str})")
    
        script_content = f"""
#!/bin/bash

myping() {{
    if ping -c{c} -w{w} $1 >/dev/null 2>&1; then echo -n "."; return 0; fi
    sleep 1
    if ping -c{c_retry} -w{w-w_retry} $1 >/dev/null 2>&1; then echo -n "o"; return 1; fi
    echo -n "X"; return 2
}}

ips=({ip_list_str})
retries=0
fails=0

for ip in "${{ips[@]}}"; do
    myping $ip
    result=$?
    if [ $result -eq 1 ]; then
        ((retries+=1))
    elif [ $result -eq 2 ]; then
        ((fails+=1))
    fi
done

echo " retries:$retries fails:$fails total:{total}"
"""
        return script_content

    def install_ping(self):
        command = "sudo apt-get update -y && sudo apt-get install -y iputils-ping"
        response = self.execute_command(command, True)
        return response
    
    def print_working_directory(self):
        directory = self.execute_command("pwd")
        print(f"Current working directory on server {self.host}: {directory}")

    def parse_packet_loss(self, output):
        """
        Parses the output to find the packet loss percentage.

        Args:
            output (str): The output string to parse.

        Returns:
            int or None: The packet loss percentage if found in the output,
            otherwise returns None.

        Example:
            >>> output = "64 bytes from 8.8.8.8: icmp_seq=1 ttl=116 time=12.5 ms, packet loss 0%"
            >>> parse_packet_loss(output)
            0
        """
        lines = output.split('\n')
        for line in lines:
            if "packet loss" in line:
                print(f"line ")
                packet_loss_str = line.split(',')[2].strip().split()[0]
                packet_loss_percentage = int(packet_loss_str[:-1])
                return packet_loss_percentage
        return None
