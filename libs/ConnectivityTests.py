import paramiko
from prometheus_client import Counter, Histogram
from libs.TimeRecorder import TimeRecorder
from libs.PrometheusExporter import CommandTypes, LabelNames


class MetricLabels:
    STATUS_CODE = 'status_code'
    HOST = 'host'
    ENDPOINT = 'endpoint'


class ResultStatusCodes:
    SUCCESS = '200'
    FAILURE = '400'


class SshClient:
    connection_count = Counter('ssh_connections_total', 'Total number of SSH connections',
                               [MetricLabels.STATUS_CODE, MetricLabels.HOST,
                                LabelNames.COMMAND_LABEL])
    connectivity_test_count = Counter('ssh_connectivity_tests_total', 'Total number of SSH connectivity tests',
                                      [MetricLabels.STATUS_CODE, MetricLabels.HOST,
                                       MetricLabels.ENDPOINT, LabelNames.COMMAND_LABEL])
    connect_duration = Histogram('ssh_connect_duration_seconds', 'Durations of SSH connections',
                                 [MetricLabels.STATUS_CODE, MetricLabels.HOST,
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
        def on_success(duration):
            self.connection_count.labels(ResultStatusCodes.SUCCESS, self.host, CommandTypes.SSH).inc()
            self.connect_duration.labels(ResultStatusCodes.SUCCESS, self.host, CommandTypes.SSH).observe(duration)

        def on_fail(duration, exception):
            self.connection_count.labels(ResultStatusCodes.FAILURE, self.host, CommandTypes.SSH).inc()
            self.connect_duration.labels(ResultStatusCodes.FAILURE, self.host, CommandTypes.SSH).observe(duration)            
        TimeRecorder.record_time(
            lambda: self.client.connect(self.host, username=self.username, pkey=self.private_key),
            on_success=on_success,
            on_fail=on_fail
        )

    def close_conn(self):
        self.client.close()

    def test_internet_connectivity(self, domain='google.com'):
        self.assertline=""
        def test_connectivity():
            script = self.create_script([domain],5,3)
            output = self.execute_command(script)
            self.ping_respond = self.parse_ping_output(output)
            if self.ping_respond != 0:
                self.connectivity_test_count.labels(ResultStatusCodes.FAILURE, self.host, domain, CommandTypes.SSH).inc()
                self.assertline=f"Failed to test internet connectivity for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}"
            else:
                self.connectivity_test_count.labels(ResultStatusCodes.SUCCESS, self.host, domain,
                                                CommandTypes.SSH).inc()
                self.assertline=f"Internet connectivity test passed for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}"
         


        def on_success(duration):
            self.connectivity_test_count.labels(ResultStatusCodes.SUCCESS, self.host, domain,
                                                CommandTypes.SSH).inc()
            self.assertline=f"Internet connectivity test passed for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}"
            
        def on_fail(duration, exception):
            self.connectivity_test_count.labels(ResultStatusCodes.FAILURE, self.host, domain, CommandTypes.SSH).inc()
            self.assertline=f"Failed to test internet connectivity for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}\nError: {exception}"

        TimeRecorder.record_time(
            test_connectivity,
            on_success=on_success,
            on_fail=on_fail
            )        
        return self.ping_respond,self.assertline


    def create_script(self,ips,c=1,w=3,c_retry=1,w_retry=3):
        total= len(ips)
        ip_list_str = ' '.join(ips)
        script_content = f"""
            #!/bin/bash

            myping() {{
                if ping -c{c} -w{w} $1 >/dev/null 2>&1; then echo return 0; fi
                sleep 1
                if ping -c{c_retry} -w{w_retry} $1 >/dev/null 2>&1; then return 1; fi
                return 2
            }}

            ips=({ip_list_str})
            retries=0
            fails=0

            for ip in "${{ips[@]}}"; do
                myping $ip
                result=$?
                echo $result
                if [ $result -eq 1 ]; then
                    ((retries+=1))
                elif [ $result -eq 2 ]; then
                    ((fails+=1))
                fi
            done

            echo " retries:$retries fails:$fails total:{total}" 
            """
        # the last echo is necessary for the parsing function, but not visible for the user
        return script_content

    def install_ping(self):
        command = "sudo apt-get update -y && sudo apt-get install -y iputils-ping"
        response = self.execute_command(command, True)
        return response
    
    def print_working_directory(self):
        directory = self.execute_command("pwd")
        print(f"Current working directory on server {self.host}: {directory}")
    
    def parse_ping_output(self, output):
        """
        Parses the output to list fails and retries.

        Args:
            output (str): The output string to parse.

        Returns:
            int or None: The packet loss percentage if found in the output,
            otherwise returns None.

        Example:
            >>> output = "X retries:0 fails:1 total:1"
            >>> parse_ping_output(output)
        """


        parts = output.split()
        try: 
            retries = int(parts[1].split(":")[1])
            fails = int(parts[2].split(":")[1])
            total = int(parts[3].split(":")[1])
            result = [retries, fails, total]
            return result
        except Exception as e:
            raise RuntimeError(f"PING output in wrong format: {e}")



# class FullConn:
#     connection_count = Counter('ssh_connections_total', 'Total number of SSH connections',
#                                [BenchMetricLabels.STATUS_CODE, BenchMetricLabels.HOST,
#                                 LabelNames.COMMAND_LABEL])
#     connectivity_test_count = Counter('vm2vm_connectivity_tests_total', 'Total number of connectivity tests',
#                                       [BenchMetricLabels.STATUS_CODE, BenchMetricLabels.HOST,
#                                        BenchMetricLabels.ENDPOINT, LabelNames.COMMAND_LABEL])
#     connect_duration = Histogram('ssh_connect_duration_seconds', 'Durations of SSH connections',
#                                  [BenchMetricLabels.STATUS_CODE, BenchMetricLabels.HOST,
#                                   LabelNames.COMMAND_LABEL])
#     def __init__(self, host, username, key_path, client):
#         self.host = host
#         self.username = username
#         self.ssh = paramiko.SSHClient()
#         policy = paramiko.AutoAddPolicy()
#         self.ssh.set_missing_host_key_policy(policy)
#         self.private_key = paramiko.RSAKey.from_private_key_file(key_path)
#         self.client = client

#     def log(self, level, message):
#         if self.logger and level >= self.min_log_level:
#             self.logger.log(level, message)

#     def collect_ips(self, client):
#         print("collecting ips")
#         ports = client.network.ports()
#         ips = []
#         for port in ports:
#             for fixed_ip in port.fixed_ips:
#                 ips.append(fixed_ip['ip_address'])
#         return ips

#     def execute_remote_command(self,port,command="self.fullconntest()", ignore_error_output=False):
#             try:
#                 self.ssh.connect(hostname=self.host, port=port, username=self.username, pkey=self.private_key)
#                 print("ssh connected")
#                 stdin, stdout, stderr = self.ssh.exec_command(command)
#                 print("execution fullconn")
#                 print(f"stdout channel {stdout}")        
#                 err_output = stderr.read().decode().strip()
#                 output = stdout.read().decode().strip()
#                 print(f"result {output}")
#                 self.ssh.close()
#                 print("ssh closed")
#                 if err_output and not ignore_error_output:
#                     raise Exception(err_output)
#                 return output

#             except Exception as e:
#                 raise RuntimeError(f"Failed to execute command '{command}' on server {self.host}: {e}")

#     def fullconntest(self, domain='google.com'):
#         self.assertline=""
#         ips = self.collect_ips()
#         total= len(ips)
#         #ips = ('8.8.8.8','10.8.3.210')
#         ip_list_str = ' '.join(ips)
        
#         self.assertline=""
#         def test_connectivity():
#             script = self.create_script([domain],5,3)
#             output = self.execute_command(script)
#             self.ping_respond = self.parse_ping_output(output)
#             if self.ping_respond != 0:
#                 self.connectivity_test_count.labels(BenchResultStatusCodes.FAILURE, self.host, domain, CommandTypes.PING).inc()
#                 self.assertline=f"Failed to test internet connectivity for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}"
#             else:
#                 self.connectivity_test_count.labels(BenchResultStatusCodes.SUCCESS, self.host, domain,
#                                                 CommandTypes.PING).inc()
#                 self.assertline=f"Internet connectivity test passed for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}"
         
#         def on_success(duration):
#             self.connectivity_test_count.labels(BenchResultStatusCodes.SUCCESS, self.host, domain,
#                                                 CommandTypes.PING).inc()
#             self.assertline=f"Internet connectivity test passed for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}"
            
#         def on_fail(duration, exception):
#             self.connectivity_test_count.labels(BenchResultStatusCodes.FAILURE, self.host, domain, CommandTypes.PING).inc()
#             self.assertline=f"Failed to test internet connectivity for server {self.host}, Domain: {domain}, Failures: {self.ping_respond[1]}, Retries: {self.ping_respond[0]}\nError: {exception}"

      
#             return self.ping_respond,self.assertline

#         def create_script(self,ips,c=1,w=3,c_retry=1,w_retry=3):
#             total= len(ips)
#             ip_list_str = ' '.join(ips)
#             print(f"VM2VM Connectivity Check ... ({ip_list_str})")
#             script_content = f"""
#                 #!/bin/bash

#                 myping() {{
#                     if ping -c{c} -w{w} $1 >/dev/null 2>&1; then echo return 0; fi
#                     sleep 1
#                     if ping -c{c_retry} -w{w_retry} $1 >/dev/null 2>&1; then return 1; fi
#                     return 2
#                 }}

#                 ips=({ip_list_str})
#                 retries=0
#                 fails=0

#                 for ip in "${{ips[@]}}"; do
#                     myping $ip
#                     result=$?
#                     echo $result
#                     if [ $result -eq 1 ]; then
#                         ((retries+=1))
#                     elif [ $result -eq 2 ]; then
#                         ((fails+=1))
#                     fi
#                 done

#                 echo " retries:$retries fails:$fails total:{total}" 
#                 """
#             # the last echo is necessary for the parsing function, but not visible for the user
#             return script_content

#         def parse_ping_output(self, output):
#             """
#             Parses the output to list fails and retries.

#             Args:
#                 output (str): The output string to parse.

#             Returns:
#                 int or None: The packet loss percentage if found in the output,
#                 otherwise returns None.

#             Example:
#                 >>> output = "X retries:0 fails:1 total:1"
#                 >>> parse_ping_output(output)
#             """


#             parts = output.split()
#             try: 
#                 retries = int(parts[1].split(":")[1])
#                 fails = int(parts[2].split(":")[1])
#                 total = int(parts[3].split(":")[1])
#                 result = [retries, fails, total]
#                 return result
#             except Exception as e:
#                 raise RuntimeError(f"PING output in wrong format: {e}")
