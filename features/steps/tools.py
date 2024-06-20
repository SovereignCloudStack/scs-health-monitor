import ipaddress
import time
from functools import wraps
import paramiko
from libs.PrometheusExporter import CommandTypes, LabelNames

import yaml
from openstack.exceptions import DuplicateResource


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


def create_vm(client, name, image_name, flavor_name, network_id, **kwargs):
    """
    Create virtual machine
    @param client: OpenStack client
    @param name: vm name
    @param image_name: image name or id to use
    @param flavor_name: flavor name or id to use
    @param network_id: network id to attach to
    @return: created vm
    """
    image = client.compute.find_image(name_or_id=image_name)
    assert image, f"Image with name {image_name} doesn't exist"
    flavor = client.compute.find_flavor(name_or_id=flavor_name)
    assert flavor, f"Flavor with name {flavor_name} doesn't exist"
    try:
        server = client.compute.create_server(
            name=name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network_id}],
            **kwargs
        )
        client.compute.wait_for_server(server)
    except DuplicateResource as e:
        assert e, "Server already created!"
        server = None
    return server

def create_jumphost(client, name, network_name, keypair_name, vm_image, flavor_name):
    # config
    security_groups = [{"name": "ssh"}, {"name": "default"}]
    keypair_filename = f"{keypair_name}-private"

    image = client.compute.find_image(name_or_id=vm_image)
    assert image, f"Image with name {vm_image} doesn't exist"
    flavor = client.compute.find_flavor(name_or_id=flavor_name)
    assert flavor, f"Flavor with name {flavor_name} doesn't exist"
    network = client.network.find_network(network_name)
    assert network, f"Network with name {network_name} doesn't exist"
    keypair = client.compute.create_keypair(name=keypair_name)
    with open(keypair_filename, 'w') as f:
        f.write("%s" % keypair.private_key)
    os.chmod(keypair_filename, 0o400)
    keypair = client.compute.find_keypair(keypair_name)
    assert keypair, f"Keypair with name {keypair_name} doesn't exist"
    for security_group in security_groups:
        security_group = client.network.find_security_group(security_group['name'])
        assert security_group, f"Security Group with name {security_group['name']} doesn't exist"

    server = client.compute.create_server(
        name=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
        key_name=keypair.name,
        security_groups=security_groups,
    )
    server = client.compute.wait_for_server(server)
    created_jumphost = client.compute.find_server(name_or_id=name)
    assert created_jumphost, f"Jumphost with name {name} was not created successfully"
    return created_jumphost

def create_network(client, name, **kwargs):
    """
    Create network
    @param client: OpenStack client
    @param name: network name
    @param kwargs: additional arguments to be passed to resource create command
    @return: created network
    """
    network = client.network.create_network(name=name, **kwargs)
    assert not client.network.find_network(
        name_or_id=network), f"Network called {network} not present!"
    return network

def list_networks(client, filter: dict=None) -> list:
    return list(client.list_networks(filter))

def create_subnet(client, name, network_id, ip_version=4, **kwargs):
    """
    Create subnet and check whether it was created
    @param network_id: network (UUID) the subnet should belong to
    @param ip_version: ip version
    @param client: OpenStack client
    @param name: router name
    @param kwargs: additional arguments to be passed to resource create command
    @return: created subnet
    """
    subnet = client.network.create_subnet(name=name, **kwargs)
    time.sleep(5)
    assert not client.network.find_network(name_or_id=subnet), \
        f"Failed to create subnet with name {subnet}"
    return subnet

def create_router(client, name, **kwargs):
    """
    Create router
    @type kwargs: additional arguments to be passed to resource create command
    @param client: OpenStack client
    @param name: router name
    @return created router
    """
    return client.network.create_router(name=name, **kwargs)

# def get_availability_zones(client):
#     return client.network.availability_zones()
def get_availability_zones(client) -> list:
    return list(client.network.availability_zones())

def create_lb(client, name, **kwargs):
    """
    Create Loadbalancer and wait until it's in state active
    @param client: OpenStack client
    @param name: lb name
    @param kwargs: additional arguments to be passed to resource create command
    @return created lb
    """
    print(kwargs)
    assert (client.load_balancer.create_load_balancer(name=name, **kwargs).
            provisioning_status == "PENDING_CREATE"), f"Expected LB {name} not in creation"
    lb = client.load_balancer.wait_for_load_balancer(name_or_id=name,
                                                     status='ACTIVE',
                                                     failures=['ERROR'], interval=2,
                                                     wait=300)
    assert lb.provisioning_status == "ACTIVE", f"Expected LB {name} not Active"
    assert lb.operating_status == "ONLINE", f"Expected LB {name} not Online"
    return lb
