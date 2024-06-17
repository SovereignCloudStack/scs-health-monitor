import ipaddress
import time
from functools import wraps
import paramiko
from libs.PrometheusExporter import CommandTypes, LabelNames

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
        self.virtual_machines_ip: list = list()


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


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'time taken by {func.__name__} is {end - start}')
        return result, end - start
    return wrapper


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

def collect_ips(client):
    print("collecting ips")
    ports = client.network.ports()
    ips = []
    for port in ports:
        for fixed_ip in port.fixed_ips:
            ips.append(fixed_ip['ip_address'])
    return ips

def check_security_group_exists(context, sec_group_name: str):
    """Check if security group exists

    Args:
        context: Behave context object
        sec_group_name (str): Name of security group to check
    
    Returns:
        ~openstack.network.v2.security_group.SecurityGroup: Found security group or None
    """
    return context.client.network.find_security_group(name_or_id=sec_group_name)

def check_keypair_exists(context, keypair_name: str):
    """Check if keypair exists

    Args:
        context: Behave context object
        keypair_name (str): Name of keypair to check
    
    Returns:
        ~openstack.compute.v2.keypair.Keypair: Found keypair object or None
    """
    return context.client.compute.find_keypair(name_or_id=keypair_name)

def create_security_group(context, sec_group_name: str, description: str):
    """Create security group in openstack

    Args:
        context: Behave context object
        sec_group_name (str): Name of security group
        description (str): Description of security group
    
    Returns:
        ~openstack.network.v2.security_group.SecurityGroup: The new security group or None
    """
    security_group = context.client.network.create_security_group(
                name=sec_group_name,
                description=description
            )
    context.collector.security_groups.append(security_group.id)
    assert security_group is not None, f"Security group with name {security_group.name} was not found"
    return security_group

def create_security_group_rule(context, sec_group_id: str, protocol: str, port_range_min: int = None, port_range_max: int = None, direction: str = 'ingress'):
    """Create security group rule for specified security group

    Args:
        context: Behave context object
        sec_group_id (str): ID of the security group for the rule
        protocol (str): The protocol that is matched by the security group rule
        port_range_min (int): The minimum port number in the range that is matched by the security group rule
        port_range_max (int): The maximum port number in the range that is matched by the security group rule
        direction (str): The direction in which the security group rule is applied
    
    Returns:
        ~openstack.network.v2.security_group_rule.SecurityGroupRule: The new security group rule
    """
    sec_group_rule = context.client.network.create_security_group_rule(
        security_group_id=sec_group_id,
        port_range_min=port_range_min,
        port_range_max=port_range_max,
        protocol=protocol,
        direction=direction
    )
    context.collector.security_groups_rules.append(sec_group_rule.id)
    assert sec_group_rule is not None, f"Rule for security group {sec_group_id} was not created"
    return sec_group_rule