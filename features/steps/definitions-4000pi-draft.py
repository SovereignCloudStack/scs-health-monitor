from behave import given, when, then
import openstack
import paramiko
import os
import time
import random
import string
import re

from openstack.exceptions import DuplicateResource

import tools

class StepsDef:

    collector = tools.Collector()

    @given("I connect to OpenStack")
    def given_i_connect_to_openstack(context):
        cloud_name = context.env.get("CLOUD_NAME")
        context.test_name = context.env.get("TESTS_NAME_IDENTIFICATION", "scs-hm")
        context.vm_image = context.env.get("VM_IMAGE")
        context.flavor_name = context.env.get("FLAVOR_NAME")
        context.client = openstack.connect(cloud=cloud_name)

    @then("I should be able to create a jumphost with name {jumphost_name}")
    def create_a_jumphost(context, jumphost_name: str):
        server = context.client.network.find_network(name_or_id=jumphost_name)
        assert server is None, f"Jumphost with {jumphost_name} already exists"
        jumphost = context.client.compute.create_server(name=jumphost_name)
        context.collector.jumphosts.append(jumphost.id)
        context.client.network.delete_network(server)
        assert context.client.network.find_network(name_or_id=server), f"Jumphost called {jumphost_name} created"

    @then("I should be able to benchmark 4000 digits of Pi on each jumphost")
    def benchmark_pi_on_jumphosts(context):
        results = []
        private_key_path = os.path.join(context.env.get("DATADIR"), context.env.get("KEYPAIRS"))
        for jumphost in context.collector.jumphosts:
            ip_address = jumphost.addresses[context.test_name][0]['addr']
            command = "{ TIMEFORMAT='%2U'; time echo 'scale=4000; 4*a(1)' | bc -l; } 2>&1"
            start_time = time.time()

            result = context.execute_remote_command(
                ip_address,
                22,
                context.env.get("DEFLTUSER"),
                private_key_path,
                command)
            print(result)
            end_time = time.time()
            duration = end_time - start_time
            print(f"Jumphost {jumphost.name} ({ip_address}): {duration:.2f} s")
            results.append((jumphost.name, ip_address, duration))

        context.log_results(results)

    def execute_remote_command(context, host, port, username, private_key_path, command):
        key = paramiko.RSAKey(filename=private_key_path)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, pkey=key)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode().strip()
        ssh.close()
        return result

    def log_results(context, results):
        with open('jumphost_benchmark_results.log', 'w') as log_file:
            for result in results:
                jumphost_name, ip_address, duration = result
                log_file.write(f"Jumphost {jumphost_name} ({ip_address}): {duration:.2f} s\n")
