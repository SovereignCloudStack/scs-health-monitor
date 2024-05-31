from behave import given, when, then
import time
from libs.SshClient import SshClient

from openstack.exceptions import DuplicateResource

import tools

class StepsDef:

    collector = tools.Collector()

    @then("I should be able to benchmark 4000 digits of Pi on each VM")
    def benchmark_pi_on_vms(context):
        results = []
        for ip in context.vm_ips[:context.jh_quantity]:
            command = "{ TIMEFORMAT='%2U'; time echo 'scale=4000; 4*a(1)' | bc -l; } 2>&1"
            start_time = time.time()
            context.ssh_client.connect()
            try:
                result = context.ssh_client.execute_command(command)
            finally:
                context.ssh_client.close_conn()
            end_time = time.time()
            duration = end_time - start_time
            results.append((ip, duration))
        context.log_results(results)

    def log_results(context, results):
        with open('pi_benchmark_results.log', 'w') as log_file:
            for result in results:
                ip, duration = result
                log_file.write(f"VM {ip}: {duration:.2f} s\n")