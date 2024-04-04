from behave import given, then
from libs.SshClient import SshClient
import os


class SshStepsDef:
    @given("I have deployed a VM with IP {vm_ip_address}")
    def initialize(context, vm_ip_address: str):
        context.vm_ip_address = vm_ip_address
        assert True
    
    @given("I have a private key at {vm_private_ssh_key_path}")
    def check_private_key_exists(context, vm_private_ssh_key_path: str):
        # Check if file exists
        context.vm_private_ssh_key_path = vm_private_ssh_key_path
        assert os.path.isfile(vm_private_ssh_key_path)
    
    @then("I should be able to SSH into the VM as user {username}")
    def test_ssh_connection(context, username):
        # Create an instance of SshClient
        ssh_client = SshClient(context.vm_ip_address, username, context.vm_private_ssh_key_path)
        # Connect to the SSH server
        ssh_client.connect()
        context.ssh_client = ssh_client

    @then("be able to communicate with the internet")
    def test_internet_connectivity(context):
        context.ssh_client.test_internet_connectivity()

    @then("be able to communicate with {domain}")
    def test_domain_connectivity(context, domain: str):
        context.ssh_client.test_internet_connectivity(domain)

    @then("close the connection")
    def close_connection(context):
        context.ssh_client.close_conn()