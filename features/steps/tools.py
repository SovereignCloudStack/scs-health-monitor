import ipaddress
import paramiko

import yaml


class Collector:

    def __init__(self):
        self.networks: list = list()
        self.subnets: list = list()
        self.routers: list = list()
        self.jumphosts: list = list()
        self.floating_ips: list = list()
        self.security_groups: list = list()
        self.security_groups_rules: list = list()
        self.virtual_machines: list = list()
        self.volumes: list = list()
        self.load_balancers: list = list()
        self.ports: list = list()
        self.enabled_ports: list = ()
        self.disabled_ports: list = list()


class Tools:

    @staticmethod
    def load_env_from_yaml():
        with open("./env.yaml", 'r+') as file:
            env = yaml.safe_load(file)
        return env

    @staticmethod
    def env_is_true(value):

        if value is None:
            return False
        elif isinstance(value, bool):
            return value
        # If the value is a string, check if it is 'True' (case insensitive)
        elif isinstance(value, str):
            return value.lower() == 'true'
        # Otherwise, default to False
        else:
            return False


def create_subnets(num):
    subnet_list = []
    ip_addresses = [
        '10.30.40.0/24',
        '192.168.200.0/24',
        '172.20.0.0/24',
        '10.40.50.0/24',
        '192.168.150.0/24',
        '10.50.60.0/24',
        '192.168.75.0/24',
        '172.30.0.0/24',
        '10.60.70.0/24',
        '192.168.250.0/24'
    ]
    quantity = 0
    for ip_address in ip_addresses:
        if quantity <= num:
            ip, default_subnet_mask = ip_address.split('/')[0], ip_address.split('/')[1]
            network = ipaddress.IPv4Network(f'{ip}/{default_subnet_mask}', strict=False)
            subnet_prefix_length = network.prefixlen + 1
            subnets = list(network.subnets(prefixlen_diff=subnet_prefix_length - network.prefixlen))
            subnets_cidr = [str(subnet.network_address) + '/' + str(subnet.prefixlen) for subnet in subnets[:3]]
            subnet_list.extend(subnets_cidr)
        else:
            break
    return subnet_list


def delete_subent_ports(client, subnet_id=None):
    for port in client.network.ports(network_id=subnet_id):
        for fixed_ip in port.fixed_ips:
            if fixed_ip['subnet_id'] == subnet_id:
                try:
                    client.network.delete_port(port.id)
                except Exception as e:
                    return f"ports on subnet with id: {subnet_id} can't be deleted because exception {e} is raised."


def ensure_volume_exist(client, volume_name: str, size: int = 10, interval: int = 2, wait: int = 120,
                        test_name: str = "scs-hm"):
    if check_volumes_created(client=client, test_name=test_name) == "available":
        volumes = list(client.block_store.volumes(name=volume_name))
        if not volumes:
            volume = client.block_store.create_volume(size=size, name=volume_name)
            client.block_store.wait_for_status(volume, 'available', interval=interval, wait=wait)


def verify_volumes_deleted(client, test_name):
    volumes_test = [volume for volume in client.block_store.volumes() if f"{test_name}-volume" in volume.name]
    assert len(volumes_test) == 0, "Some volumes still exist"

def verify_volume_deleted(client, volume_id):
    assert not client.block_store.find_volume(name_or_id=volume_id), f"Volume with ID {volume_id} was not deleted"

def verify_router_deleted(client, router_id):
    assert not client.network.find_router(name_or_id=router_id), f"Router with ID {router_id} was not deleted"

def check_volumes_created(client, test_name):
    for volume in client.volume.volumes():
        if test_name in volume.name:
            volume = client.block_store.wait_for_status(volume, 'available', interval=2, wait=120)
            assert volume.status == 'available', f"Volume {volume.name} not available"
            return volume.status


# Collect IPs from OpenStack
def collect_ips(client):
    print("collecting ips")
    ports = client.network.ports()
    ips = []
    for port in ports:
        for fixed_ip in port.fixed_ips:
            ips.append(fixed_ip['ip_address'])
    return ips

# Remote command execution
def execute_remote_command(host, port, username, private_key_path):
    key = paramiko.RSAKey(filename=private_key_path)
    print("key")
    ssh = paramiko.SSHClient()
    print("ssh-client")
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("set_missing_host_key_policy")
    ssh.connect(hostname=host, port=port, username=username, pkey=key)
    print("ssh connected")
    stdin, stdout, stderr = ssh.exec_command(fullconntest())
    #stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"from __main__ import fullconntest; fullconntest()\"")

    print("execution fullconn")
    print(f"stdout channel {stdout}")
    result = stdout.read().decode().strip()
    print(f"result {result}")
    ssh.close()
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

