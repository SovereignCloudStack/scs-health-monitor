import ipaddress

import yaml
from openstack.network.v2._proxy import Proxy
from pprint import pprint


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


def ensure_volume_exist(client, volume_name: str, quantity: int, size: int = 10, interval: int = 2, wait: int = 120):
    volumes = list(client.block_store.volumes(name=volume_name))
    if not volumes:
        volume = client.block_store.create_volume(size=size, name=volume_name)
        client.block_store.wait_for_status(volume, 'available', interval=interval, wait=wait)


def verify_volumes_deleted(client, test_name):
    volumes_test = [volume for volume in client.block_store.volumes() if f"{test_name}-volume" in volume.name]
    pprint(volumes_test)
    assert len(volumes_test) == 0, "Some volumes still exist"

