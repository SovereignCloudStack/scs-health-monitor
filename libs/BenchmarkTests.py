import paramiko
from prometheus_client import Counter, Histogram
from libs.TimeRecorder import TimeRecorder
from libs.PrometheusExporter import CommandTypes, LabelNames


class BenchMetricLabels:
    STATUS_CODE = 'status_code'
    HOST = 'host'
    ENDPOINT = 'endpoint'


class BenchResultStatusCodes:
    SUCCESS = '200'
    FAILURE = '400'

class FullConn:
    connection_count = Counter('ssh_connections_total', 'Total number of SSH connections',
                               [BenchMetricLabels.STATUS_CODE, BenchMetricLabels.HOST,
                                LabelNames.COMMAND_LABEL])
    connectivity_test_count = Counter('vm2vm_connectivity_tests_total', 'Total number of connectivity tests',
                                      [BenchMetricLabels.STATUS_CODE, BenchMetricLabels.HOST,
                                       BenchMetricLabels.ENDPOINT, LabelNames.COMMAND_LABEL])
    connect_duration = Histogram('ssh_connect_duration_seconds', 'Durations of SSH connections',
                                 [BenchMetricLabels.STATUS_CODE, BenchMetricLabels.HOST,
                                  LabelNames.COMMAND_LABEL])
    def __init__(self, host, username, key_path, client):
        self.host = host
        self.username = username
        self.ssh = paramiko.SSHClient()
        policy = paramiko.AutoAddPolicy()
        self.ssh.set_missing_host_key_policy(policy)
        self.private_key = paramiko.RSAKey.from_private_key_file(key_path)
        self.client = client

    def collect_ips(self, client):
        print("collecting ips")
        ports = client.network.ports()
        ips = []
        for port in ports:
            for fixed_ip in port.fixed_ips:
                ips.append(fixed_ip['ip_address'])
        return ips

    # Remote command execution
    def execute_remote_command(self, port):
        self.ssh.connect(hostname=self.host, port=port, username=self.username, pkey=self.private_key)
        print("ssh connected")
        stdin, stdout, stderr = self.ssh.exec_command(self.fullconntest())
        #stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"from __main__ import fullconntest; fullconntest()\"")

        print("execution fullconn")
        print(f"stdout channel {stdout}")
        result = stdout.read().decode().strip()
        print(f"result {result}")
        self.ssh.close()
        print("ssh closed")
        return result

    # Main function to perform connectivity check
    def fullconntest():
        ips = collect_ips()
        total= len(ips)
        #ips = ('8.8.8.8','10.8.3.210')
        ip_list_str = ' '.join(ips)
        print(f"VM2VM Connectivity Check ... ({ip_list_str})")
        
        script_content = f"""
        #!/bin/bash

        myping() {{
            if ping -c1 -w1 $1 >/dev/null 2>&1; then echo -n "."; return 0; fi
            sleep 1
            if ping -c1 -w3 $1 >/dev/null 2>&1; then echo -n "o"; return 1; fi
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

        echo " retries: $retries fails: $fails total: {total}"
    """
        return script_content


    if __name__ == "__main__":
        # Configure your SSH parameters
        FLOATS = ['localhost','localhost','localhost'] #'213.131.230.89'
        JHNO = 1 # TODO: generic read jump host quantity
        DEFLTUSER = context['DEFLTUSER']
        DATADIR = context['DATADIR']
        KEYPAIRS = [context['KEYPAIRS']]
        REDIRS = [['tcp,22'],['tcp,22'],['tcp,22']] # TODO: generic 

        for jhno in range(JHNO):
                print(f"iteration {jhno}")
                for red in REDIRS[jhno]:
                    port = int(red.split(',')[1])
                    print(f"port {port}")
                    command = f"python3 -c \"from __main__ import fullconntest; fullconntest()\""
                    result = execute_remote_command(FLOATS[jhno], port, DEFLTUSER, os.path.join(DATADIR, KEYPAIRS[jhno]))
                    