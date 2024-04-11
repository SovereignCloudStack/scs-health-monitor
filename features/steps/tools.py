import ipaddress

import yaml
from openstack.network.v2._proxy import Proxy


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
        '10.30.40.0',
        '192.168.200.0',
        '172.20.0.0',
        '10.40.50.0',
        '192.168.150.0',
        '10.50.60.0',
        '192.168.75.0',
        '172.30.0.0',
        '10.60.70.0',
        '192.168.250.0'
    ]
    quantity = 0
    for ip_address in ip_addresses:
        if quantity <= num:
            default_subnet_mask = '24'
            network = ipaddress.IPv4Network(f'{ip_address}/{default_subnet_mask}', strict=False)
            subnet_prefix_length = network.prefixlen + 1
            subnets = list(network.subnets(prefixlen_diff=subnet_prefix_length - network.prefixlen))
            subnets_cidr = [str(subnet.network_address) + '/' + str(subnet.prefixlen) for subnet in subnets[:3]]
            subnet_list.extend(subnets_cidr)
        else:
            break
    return subnet_list
