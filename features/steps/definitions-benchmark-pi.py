from behave import given, when, then
import time

import tools

class StepsDef:
    collector = tools.Collector()

    @then("I should be able to calculate 4000 digits of Pi on each VM and measure time")
    def benchmark_pi_on_vms(context):
        results = []
        for ip in context.ips:
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
