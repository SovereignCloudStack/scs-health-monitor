import ipaddress
import time
import datetime
from functools import wraps
from typing import Iterator

from openstack.compute.v2.server import Server
from openstack.network.v2.floating_ip import FloatingIP
from openstack.network.v2.network import Network

from libs.loggerClass import Logger
from concurrent.futures import ThreadPoolExecutor
import os
import re

import yaml
from openstack.exceptions import DuplicateResource
import openstack
from prometheus_client import Gauge


class Collector:

    def __init__(self, client: openstack.connection.Connection = None):
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
        # List of routers and their subnets. dicts {"router": <router-id>, "subnet": <subnet-id>}
        self.router_subnets: list[dict] = list()
        self.enabled_ports: list = ()
        self.disabled_ports: list = list()
        self.virtual_machines_ip: list = list()

        self.client = client

    def __bool__(self):
        return any(
            (
                self.networks,
                self.subnets,
                self.routers,
                self.jumphosts,
                self.floating_ips,
                self.security_groups,
                self.security_groups_rules,
                self.virtual_machines,
                self.volumes,
                self.load_balancers,
                self.ports,
                self.enabled_ports,
                self.disabled_ports,
                self.virtual_machines_ip,
            )
        )

    def create_router(self, name, **kwargs):
        """
        Create a new router and add its ID to the list of routers

        Args:
            name (str): The name of the router to be created
            **kwargs: Additional parameters to be passed to the `create_router` function
        Returns:
            router (dict): router object
        """
        router = create_router(self.client, name, **kwargs)
        self.routers.append(router.id)
        return router

    def create_network(self, name, **kwargs):
        """
        Create a new network and add its ID to the list of network

        Args:
            name (str): The name of the router to be created.
            **kwargs: Additional parameters to be passed to the `create_network` function
        Returns:
            net (dict): network object
        """
        net = create_network(self.client, name, **kwargs)
        self.networks.append(net.id)
        return net

    def create_subnet(self, name, network_id, ip_version=4, **kwargs):
        """
        Create a new subnet and add its ID to the list of subnets

        Args:
            name (str): The name of the subnet to be created
            network_id (str): The ID of the network to which the subnet will be associated
            ip_version (int, optional): The IP version for the subnet (default is 4)
            **kwargs: Additional parameters to be passed to the `create_subnet` function

        Returns:
            subnet (dict): The subnet object created by the `create_subnet` function
        """
        subnet = create_subnet(self.client, name, network_id, ip_version, **kwargs)
        self.subnets.append(subnet.id)
        return subnet

    def add_interface_to_router(self, router, subnet_id):
        """
        Add a subnet interface to a router and track the association

        Args:
            router (dict): The router object to which the subnet interface will be added
            subnet_id (str): The ID of the subnet to be attached to the router

        Returns:
            router_update (dict): The updated router object after adding the interface
            by the `add_interface_to_router` function
        """
        router_update = add_interface_to_router(self.client, router, subnet_id)
        self.router_subnets.append({"router": router.id, "subnet": subnet_id})
        return router_update

    def find_router(self, name_or_id):
        """
        Find and retrieve a router by its name or ID

        Args:
            name_or_id (str): The name or ID of the router to be found

        Returns:
            dict: The router object if found by the `find_router` function

        Example:
            >>> router = instance.find_router(name_or_id="new-router")
            >>> print(router["id"])
        """
        return find_router(self.client, name_or_id)

    def find_server(self, name_or_id):
        """
        Finds a server by its name or ID using the Openstack Client

        Args:
            name_or_id (str): The name or ID of the server to find

        Returns:
            object: The server object if found, or `None` if not found
        """
        return self.client.compute.find_server(name_or_id=name_or_id)

    def delete_router_subnets(self):
        """
        Deletes subnets from routers.

        Iterates over the router-subnet pairs stored in `self.router_subnets`, removing the subnet interface from
        each router. Upon successful removal, the pair is removed from `self.router_subnets`

        Raises:
        Exception: If removing the interface from the router fails.
        """
        for router_subnet in self.router_subnets:
            router = router_subnet["router"]
            subnet_id = router_subnet["subnet"]
            res = self.client.network.remove_interface_from_router(router, subnet_id)
            if not res:
                self.router_subnets.remove({"router": router.id, "subnet": subnet_id})

    def delete_security_groups(self):
        """
        Deletes all security groups.

        Iterates over the list of security groups stored in `self.security_groups` and deletes each one.
        The security group is removed from the list upon successful deletion.
        """
        for security_group in self.security_groups:
            self.client.network.delete_security_group(security_group)
            self.security_groups.remove(security_group)

    def create_jumphost(
        self,
        name,
        network_name,
        keypair_name,
        vm_image,
        flavor_name,
        security_groups,
        **kwargs,
    ):
        """
        Creates a new JumpHost (VM) and attaches it to the specified network

        Args:
            name (str): The name of the JumpHost to create
            network_name (str): The name of the network to which the JumpHost will be attached
            keypair_name (str): The name of the keypair to be used for the JumpHost
            vm_image (str): The image to use for the VM
            flavor_name (str): The flavor to use for the VM (i.e., the size of the instance)
            security_groups (list): A list of security group names to associate with the JumpHost
            **kwargs: Additional keyword arguments to pass to the `create_jumphost` function

        Returns:
            object: The created VM object
        """
        vm = create_jumphost(
            self.client,
            name,
            network_name,
            keypair_name,
            vm_image,
            flavor_name,
            security_groups,
            **kwargs,
        )
        self.virtual_machines.append(vm.id)
        return vm

    def create_floating_ip(self, server_name):
        """
        Creates and attaches a floating IP to the specified server
        Finds the server by its name and attaches a newly created floating IP to it
        The floating IP is then appended to an object

        Args:
            server_name (str): The name of the server to which the floating IP will be attached.

        Returns:
            object: The floating IP object.

        Raises:
            AssertionError: If the server with the specified `server_name` is not found.
        """
        server = self.client.compute.find_server(name_or_id=server_name)
        assert server, f"Server with name {server_name} not found"
        fip = self.client.add_auto_ip(server=server, wait=True, reuse=False)
        self.floating_ips.append(fip)
        return fip

    def create_security_group(self, sec_group_name: str, description: str):
        """Create security group in openstack

        Args:
            sec_group_name (str): Name of security group
            description (str): Description of security group

        Returns:
            ~openstack.network.v2.security_group.SecurityGroup: The new security group or None
        """
        security_group = self.client.network.create_security_group(
            name=sec_group_name, description=description
        )

        assert (security_group is not None), \
            f"Security group with name {sec_group_name} could not be created"

        self.security_groups.append(security_group.id)

        return security_group

    def create_security_group_rule(
        self,
        sec_group_id: str,
        protocol: str,
        port_range_min: int = None,
        port_range_max: int = None,
        direction: str = "ingress",
        remote_ip_prefix: str = "0.0.0.0/0",
    ):
        """Create security group rule for specified security group

        Args:
            sec_group_id (str): ID of the security group for the rule
            protocol (str): The protocol that is matched by the security group rule
            port_range_min (int): The minimum port number in the range that is matched by the security group rule
            port_range_max (int): The maximum port number in the range that is matched by the security group rule
            direction (str): The direction in which the security group rule is applied
            remote_ip_prefix (str): source IP address to be associated with the rule

        Returns:
            ~openstack.network.v2.security_group_rule.SecurityGroupRule: The new security group rule
        """
        sec_group_rule = self.client.network.create_security_group_rule(
            security_group_id=sec_group_id,
            port_range_min=port_range_min,
            port_range_max=port_range_max,
            protocol=protocol,
            direction=direction,
            remote_ip_prefix=remote_ip_prefix,
        )
        self.security_groups_rules.append(sec_group_rule.id)
        assert (
            sec_group_rule is not None
        ), f"Rule for security group {sec_group_id} was not created"
        return sec_group_rule


class Tools:

    @staticmethod
    def load_env_from_yaml():
        with open("./env.yaml", "r+") as file:
            env = yaml.safe_load(file)
        return env

    @staticmethod
    def env_is_true(value):
        """
        Determine if the given value is equivalent to a boolean 'True'

        Args:
            value (str or bool or None): The value to evaluate, it can be a string, boolean, or None

        Returns:
            bool: True if the value is equivalent to 'True', otherwise False

        The function behaves as follows:
        - If the value is `None`, it returns `False`
        - If the value is a boolean, it returns the boolean value
        - If the value is a string, it returns `True` if the string is "True" (case-insensitive), otherwise `False`
        - For any other type of value, it defaults to returning `False`

        Example:
            >>> env_is_true(None)
            False
            >>> env_is_true(True)
            True
            >>> env_is_true("True")
            True
            >>> env_is_true("false")
            False
        """

        if value is None:
            return False
        elif isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() == "true"
        else:
            return False


def time_it(func):
    """
    A decorator that measures and prints the time taken by a function to execute.

    Args:
        func (callable): The function to be timed.

    Returns:
        callable: A wrapped function that, when called, executes the original function,
        prints the time taken for its execution, and returns a tuple containing the function's
        result and the time taken.

    Example:
        >>> @time_it
        ... def example_function():
        ...     time.sleep(1)
        ...     return "Done"
        >>> result, duration = example_function()
        time taken by example_function is 1.0001
        >>> print(result, duration)
        Done 1.0001
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"time taken by {func.__name__} is {end - start}")
        return result, end - start

    return wrapper


def add_value_to_dict_list(d, key, value):
    """
    Adds a value to a list in a dictionary. If the key does not exist in the dictionary,
    it initializes the key with an empty list before adding the value

    Args:
        d (dict): The dictionary where the value should be added
        key (hashable): The key in the dictionary where the value should be added
        value (any): The value to add to the list associated with the given key
    """
    if key not in d:
        d[key] = []
    d[key] = value


def create_subnets(num):
    """
    Generates a list of subnet CIDRs by splitting predefined IP address ranges

    Args:
        num (int): The number of subnet CIDRs to generate

    Returns:
        list: A list of subnet CIDRs as strings

    The function uses a predefined list of IP address ranges and splits each one into smaller subnets
    It stops generating subnets when the specified number (`num`) is reached
    """
    subnet_list = []
    ip_addresses = [
        "10.30.40.0/24",
        "192.168.200.0/24",
        "172.20.0.0/24",
        "10.40.50.0/24",
        "192.168.150.0/24",
        "10.50.60.0/24",
        "192.168.75.0/24",
        "172.30.0.0/24",
        "10.60.70.0/24",
        "192.168.250.0/24",
    ]
    quantity = 0
    for ip_address in ip_addresses:
        if quantity <= num:
            ip, default_subnet_mask = ip_address.split("/")[0], ip_address.split("/")[1]
            network = ipaddress.IPv4Network(f"{ip}/{default_subnet_mask}", strict=False)
            subnet_prefix_length = network.prefixlen + 1
            subnets = list(
                network.subnets(prefixlen_diff=subnet_prefix_length - network.prefixlen)
            )
            subnets_cidr = [
                str(subnet.network_address) + "/" + str(subnet.prefixlen)
                for subnet in subnets[:3]
            ]
            subnet_list.extend(subnets_cidr)
        else:
            break
    return subnet_list


def vm_extract_ip_by_type(server, type: str):
    """
    Iterate addresses of server object and return first floating ip we find
    Typical types are 'floating' or 'fixed'
    @param server:
    @return: floating ip or None if not present
    """
    for vm_nets in server["addresses"].values():
        for vm_addr in vm_nets:
            if vm_addr["OS-EXT-IPS:type"] == type:
                # We found an ip attached to the machine.
                return vm_addr["addr"]
    return None


def delete_subent_ports(client, subnet_id=None):
    """
    Generates a list of subnet CIDRs by splitting predefined IP address ranges
    uses a predefined list of IP address ranges and splits each one into smaller subnets until num is reached

    Args:
        num (int): The number of subnet CIDRs to generate

    Returns:
        list: A list of subnet CIDRs as strings
    """
    for port in client.network.ports(network_id=subnet_id):
        for fixed_ip in port.fixed_ips:
            if fixed_ip["subnet_id"] == subnet_id:
                try:
                    client.network.delete_port(port.id)
                except Exception as e:
                    return f"ports on subnet with id: {subnet_id} can't be deleted because exception {e} is raised."


def ensure_volume_exist(
    client,
    volume_name: str,
    size: int = 10,
    interval: int = 2,
    wait: int = 120,
    test_name: str = "scs-hm",
):
    """
    Ensures that a volume with the specified name exists and is available
    If the volume does not exist, it creates a new volume with the specified size
    and waits until it becomes available

    Args:
        client (object): The client object used to interact with the block storage service
        volume_name (str): The name of the volume to check or create
        size (int, optional): The size of the volume in GB. Defaults to 10 GB
        interval (int, optional): The time interval (in seconds) between status checks when waiting for the volume to become available. Defaults to 2 seconds
        wait (int, optional): The maximum time (in seconds) to wait for the volume to become available. Defaults to 120 seconds
        test_name (str, optional): The name used to filter the check for existing volumes. Defaults to "scs-hm"

    Returns:
        None

    Example:
        >>> ensure_volume_exist(client, volume_name="data-volume", size=20)
    """
    if check_volumes_created(client=client, test_name=test_name) == "available":
        volumes = list(client.block_store.volumes(name=volume_name))
        if not volumes:
            volume = client.block_store.create_volume(size=size, name=volume_name)
            client.block_store.wait_for_status(
                volume, "available", interval=interval, wait=wait
            )


def verify_volumes_deleted(client, test_name):
    """
    Verifies that all volumes associated with the given test name have been deleted
    from the block storage service

    Args:
        client (object): The client object used to interact with the block storage service
        test_name (str): The name prefix used to identify volumes related to the test

    Raises:
        AssertionError: If any volumes associated with the `test_name` are still found
    """
    volumes_test = [
        volume
        for volume in client.block_store.volumes()
        if f"{test_name}-volume" in volume.name
    ]
    assert len(volumes_test) == 0, "Some volumes still exist"


def verify_volume_deleted(client, volume_id):
    """
    Verifies that a volume associated with the given volume_id has been deleted
    from the block storage service

    Args:
        client (object): The client object used to interact with the block storage service
        volume_id (str): The ID of the volume to verify deletion

    Raises:
        AssertionError: If the volume with the specified `volume_id` still exists
    """
    assert not client.block_store.find_volume(
        name_or_id=volume_id
    ), f"Volume with ID {volume_id} was not deleted"


def verify_router_deleted(client, router_id):
    """
    Verifies that a specific router in the network service has been deleted

    Args:
        client (object): The client object used to interact with the network service
        router_id (str): The ID of the router to verify deletion

    Raises:
        AssertionError: If the router with the specified `router_id` still exists
    """
    assert not client.network.find_router(
        name_or_id=router_id
    ), f"Router with ID {router_id} was not deleted"


def check_volumes_created(client, test_name):
    """
    Checks if volumes associated with the given test name have been created and are available
    If found, it waits until the volume's status is 'available' and returns that status
    An assertion error is raised if the volume does not reach the 'available' status

    Args:
        client (object): The client object used to interact with the block storage service.
        test_name (str): The name prefix used to identify volumes related to the test.

    Returns:
        str: The status of the volume if it is available

    Raises:
        AssertionError: If the volume is not in the 'available' status

    """
    for volume in client.volume.volumes():
        if test_name in volume.name:
            volume = client.block_store.wait_for_status(
                volume, "available", interval=2, wait=120
            )
            assert volume.status == "available", f"Volume {volume.name} not available"
            return volume.status


def attach_floating_ip_to_server(context, server_name) -> FloatingIP:
    """
    Attaches a floating IP to the specified server and adds it to the context

    Args:
        context (object): The context object containing the client and logger
        server_name (str): The name of the server to which the floating IP will be attached

    Returns:
        tuple: A tuple containing the floating IP and an assert line if an error occurred
    """
    server: Server = context.client.compute.find_server(name_or_id=server_name)
    assert server is not None

    # Find all available networks that are marked as "external" (connection to outside the cluster)
    external_networks: Iterator[Network] = context.client.network.networks(is_router_external=True)

    # Then iterate over them and take one as floating IP source pool
    counter_external_networks = 0
    chosen_external_network: Network | None = None
    for network in external_networks:
        context.logger.log_info(f"Network in external_networks: {network}")
        counter_external_networks += 1
        chosen_external_network = network

    # Checking the counter and the chosen network might be redundant, but you cannot
    # count the len() of the iterator above. We want to make sure both cases are tested.
    assert counter_external_networks > 0, "There are no external facing networks available"
    assert chosen_external_network is not None

    fip: FloatingIP = context.client.create_floating_ip(
        network=chosen_external_network.id,
        server=server,
        wait=True,
        timeout=60)
    assert fip is not None

    context.fip_address = fip.floating_ip_address
    context.logger.log_info(f"Attached floating ip: {fip}")

    context.collector.floating_ips.append(fip.id)

    return fip


def collect_float_ips(client, logger: Logger):
    """
    Retrieves all floating IPs available in the network service, logs each floating IP found
    If no floating IPs are found, it returns an assert line

    Args:
        client (object): The client object used to interact with the network service
        logger (Logger): The logger object used to log debug information

    Returns:
        tuple: A tuple containing a list of floating IPs and an assert line if no IPs were found
    """
    ips = []
    assertline = None
    floating_ips = client.network.ips()
    for ip in floating_ips:
        ips.append(ip.floating_ip_address)
        logger.log_debug(f"found floating ip {ip.floating_ip_address}")
    if len(ips) == 0:
        assertline = f"No ips found"
    return ips, assertline


def collect_ips(redirs, test_name, logger: Logger):
    """
    Extracts IP addresses from GIVEN dictionary for VMs associated with the specified prefix

    Args:
        redirs (dict): The dictionary containing redirection data
        test_name (str): The name of the test to collect IPs for
        logger (Logger): The logger object used to log information

    Returns:
        tuple: A tuple containing a list of IPs and an assert line if no IPs were found
    """
    assertline = None
    ips = [vm["addr"] for vm in redirs[f"{test_name}jh0"]["vms"]]
    if len(ips) == 0:
        assertline = f"No ips found"
    return ips, assertline


def collect_jhs(redirs, test_name, logger: Logger):
    """
    Extracts JumpHost (JH) IP addresses from the given redirection data for a specific test name
    uses regular expressions to validate and extract IP addresses from the provided data

    Args:
        redirs (dict): The dictionary containing redirection data
        test_name (str): The name of the test to collect JumpHost IPs for
        logger (Logger): The logger object used to log information

    Returns:
        list: A list of JumpHost IP addresses
    """
    ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    strip_pattern = re.compile(r"'([^']+)'")
    jhs = []
    for key, value in redirs.items():
        if f"{test_name}jh" in key and "fip" in value:
            ip_string = value["fip"]
            strip_me = strip_pattern.search(ip_string)
            if strip_me:
                ip_string = strip_me.group(1)
            ip_valid = ip_pattern.search(ip_string)
            if ip_valid:
                jhs.append(ip_valid.group(1))
    logger.log_info(f"returning jhs: {jhs}")
    return jhs


def get_floating_ip_id(context, floating_ip: str) -> str | None:
    """Get ID of floating IP based on its address.

    Args:
        context: Behave context object.
        floating_ip: Floating IP address value.

    Returns:
        ID of the floating IP or None if not found.
    """
    floating_ip_list = context.client.list_floating_ips()
    for fl_ip in floating_ip_list:
        if fl_ip.floating_ip_address == floating_ip:
            return fl_ip.id
    return None


def check_security_group_exists(context, sec_group_name: str):
    """Check if security group exists.

    Args:
        context: Behave context object.
        sec_group_name: Name of security group to check.

    Returns:
        ~openstack.network.v2.security_group.SecurityGroup: Found security group or None.
    """
    return context.client.network.find_security_group(name_or_id=sec_group_name)


def check_keypair_exists(client, keypair_name: str):
    """Check if keypair exists.

    Args:
        client: OpenStack client
        keypair_name: Name of keypair to check.

    Returns:
        ~openstack.compute.v2.keypair.Keypair: Found keypair object or None.
    """
    return client.compute.find_keypair(name_or_id=keypair_name)


def create_security_group(context, sec_group_name: str, description: str):
    """Create security group in openstack.

    Args:
        context: Behave context object.
        sec_group_name: Name of security group.
        description: Description of security group.

    Returns:
        ~openstack.network.v2.security_group.SecurityGroup: The new security group or None.
    """
    security_group = context.client.network.create_security_group(
        name=sec_group_name, description=description
    )
    context.collector.security_groups.append(security_group.id)
    assert (
        security_group is not None
    ), f"Security group with name {security_group.name} was not found"
    return security_group


def create_security_group_rule(
    context,
    sec_group_id: str,
    protocol: str,
    port_range_min: int = None,
    port_range_max: int = None,
    direction: str = "ingress",
):
    """Create security group rule for specified security group.

    Args:
        context: Behave context object.
        sec_group_id: ID of the security group for the rule.
        protocol: The protocol that is matched by the security group rule.
        port_range_min: The minimum port number in the range that is matched by the security group rule.
        port_range_max: The maximum port number in the range that is matched by the security group rule.
        direction: The direction in which the security group rule is applied.

    Returns:
        ~openstack.network.v2.security_group_rule.SecurityGroupRule: The new security group rule.
    """
    sec_group_rule = context.client.network.create_security_group_rule(
        security_group_id=sec_group_id,
        port_range_min=port_range_min,
        port_range_max=port_range_max,
        protocol=protocol,
        direction=direction,
    )
    context.collector.security_groups_rules.append(sec_group_rule.id)
    assert (
        sec_group_rule is not None
    ), f"Rule for security group {sec_group_id} was not created"
    return sec_group_rule


def create_wait_script(conn_test, testname):
    """
    creates temp script locally and makes it executable
    script checks if the command $1 exists, waits for the system boot to finish
    if necessary and retries for up to 100 seconds if the command is not found

        not in use for now
    """
    assertline = None
    script_path = f"{testname}-wait"
    secondary = None
    if "iperf" in conn_test:
        secondary = "iperf"

    script_content = f"""
            #!/bin/bash
            let MAXW=100
            if test ! -f /var/lib/cloud/instance/boot-finished; then sleep 5; sync; fi
            while test \$MAXW -ge 1; do
            if type -p "{conn_test}">/dev/null || type -p "{secondary}">/dev/null; then exit 0; fi
            let MAXW-=1
            sleep 1
            if test ! -f /var/lib/cloud/instance/boot-finished; then sleep 1; fi
            done
            exit 1
            """
    try:
        with open(script_path, "w") as file:
            file.write(script_content)
        os.chmod(script_path, 0o755)
    except:
        assertline = f"Failed to write script file {script_path}"
    return assertline


def delete_wait_script(testname):
    assertline = None
    script_path = f"{testname}-wait"
    try:
        os.remove(script_path)
    except:
        assertline = f"Failed to delete script file {script_path}"
    return assertline


def delete_vms(context, vm_ids: list = None):
    """Delete VMs based on list of IDs or VM IDs in collector.

    Args:
        context: Behave context object.
        vm_ids: List of VM IDs to delete, if None, collector VM IDs are used.
    """
    vm_ids = context.collector.virtual_machines[:] if not vm_ids else vm_ids
    if vm_ids:
        context.logger.log_info(f"VMs to delete: {vm_ids}")
        for vm_id in vm_ids:
            if context.client.delete_server(vm_id, wait=True):
                context.logger.log_info(f"VM {vm_id} deleted")
                try:
                    context.collector.virtual_machines.remove(vm_id)
                except ValueError:
                    if vm_id in context.collector.jumphosts:
                        context.collector.jumphosts.remove(vm_id)
            else:
                context.logger.log_info(f"VM {vm_id} wasn't deleted")


def delete_routers(context, router_ids: list = None):
    """Delete routers based on list of IDs or router IDs in collector.

    Args:
        context: Behave context object.
        router_ids: List of router IDs to delete, if None, collector router IDs are used.
    """
    router_ids = context.collector.routers[:] if not router_ids else router_ids
    if router_ids:
        context.logger.log_info(f"Routers to delete: {router_ids}")
        for router_id in router_ids:
            if context.client.delete_router(router_id):
                context.logger.log_info(f"Router {router_id} deleted")
                context.collector.routers.remove(router_id)
            else:
                context.logger.log_info(f"Router {router_id} wasn't deleted")


def delete_networks(context, network_ids: list = None):
    """Delete networks based on list of IDs or network IDs in collector.

    Args:
        context: Behave context object.
        network_ids: List of network IDs to delete, if None, collector network IDs are used.
    """
    network_ids = context.collector.networks[:] if not network_ids else network_ids
    if network_ids:
        context.logger.log_info(f"Networks to delete: {network_ids}")
        for network_id in network_ids:
            if context.client.delete_network(network_id):
                context.logger.log_info(f"Network {network_id} deleted")
                context.collector.networks.remove(network_id)
            else:
                context.logger.log_info(f"Network {network_id} wasn't deleted")


def delete_subnets(context, subnet_ids: list = None):
    """Delete subnets based on list of IDs or subnet IDs in collector.

    Args:
        context: Behave context object.
        subnet_ids: List of subnet IDs to delete, if None, collector subnet IDs are used.
    """
    subnet_ids = context.collector.subnets[:] if not subnet_ids else subnet_ids
    if subnet_ids:
        context.logger.log_info(f"Subnets to delete: {subnet_ids}")
        for subnet_id in subnet_ids:
            if context.client.delete_subnet(subnet_id):
                context.logger.log_info(f"Subnet {subnet_id} deleted")
                context.collector.subnets.remove(subnet_id)
            else:
                context.logger.log_info(f"Subnet {subnet_id} wasn't deleted")


def delete_ports(context, port_ids: list = None):
    """Delete ports based on list of IDs or port IDs in collector.

    Args:
        context: Behave context object.
        port_ids: List of port IDs to delete, if None, collector port IDs are used.
    """
    port_ids = context.collector.ports[:] if not port_ids else port_ids
    if port_ids:
        context.logger.log_info(f"Ports to delete: {port_ids}")
        for port_id in port_ids:
            if context.client.delete_port(port_id):
                context.logger.log_info(f"Port {port_id} deleted")
                context.collector.ports.remove(port_id)
            else:
                context.logger.log_info(f"Port {port_id} wasn't deleted")


def delete_floating_ips(context, floating_ip_ids: list = None):
    """Delete floating IPs based on list of IDs or floating IP IDs in collector.

    Args:
        context: Behave context object.
        floating_ip_ids: List of floating IP IDs to delete, if None, collector floating IP IDs are used.
    """
    floating_ip_ids = (
        context.collector.floating_ips[:] if not floating_ip_ids else floating_ip_ids
    )
    if floating_ip_ids:
        context.logger.log_info(f"Floating IPs to delete: {floating_ip_ids}")
        for fl_ip_id in floating_ip_ids:
            if context.client.delete_floating_ip(fl_ip_id):
                context.logger.log_info(f"Floating ip {fl_ip_id} deleted")
                context.collector.floating_ips.remove(fl_ip_id)
            else:
                context.logger.log_info(f"Floating ip {fl_ip_id} wasn't deleted")


def delete_jumphosts(context, jumphost_ids: list = None):
    """Delete jumphosts based on list of IDs or jumphost IDs in collector.

    Args:
        context: Behave context object.
        jumphost_ids: List of jumphost IDs to delete, if None, collector jumphost IDs are used.
    """
    jumphost_ids = context.collector.jumphosts[:] if not jumphost_ids else jumphost_ids
    delete_vms(context, jumphost_ids)


def delete_all_test_resources(context):
    """Delete all resources used in the feature run.

    Args:
        context: Behave context object
    """
    delete_vms(context)
    delete_jumphosts(context)
    delete_ports(context)
    context.collector.delete_router_subnets()
    delete_floating_ips(context)
    delete_subnets(context)
    delete_networks(context)
    delete_routers(context)
    context.collector.delete_security_groups()


def parse_ping_output(context, data: list[str], logger: Logger):
    """Parse the outputs of the ping response test, print them to logger and add them to prometheus exporter registry.

    Args:
        context: Behave context object.
        data: Ssh command stdout data.
        logger: Default context logger.
    """
    start_time, end_time = get_timestamps(data[0])
    calc_time = int(end_time) - int(start_time)
    start_time = datetime.datetime.fromtimestamp(int(start_time))
    end_time = datetime.datetime.fromtimestamp(int(end_time))
    ping_data = data[1].split(sep="\n")
    response_times = []
    for ping_res in ping_data:
        split_ping_res = ping_res.split()
        timestamp = split_ping_res[0][1:11:1]
        timestamp = datetime.datetime.fromtimestamp(int(timestamp))
        if timestamp >= start_time and timestamp <= end_time:
            response_times.append(float(split_ping_res[1].split(sep="=")[1]))
    logger.log_info(f"Average response time is: {calc_average(response_times)} ms")
    logger.log_info(f"Num of values: {len(response_times)}")
    logger.log_info(f"Calc start: {start_time}")
    logger.log_info(f"Calc ended: {end_time}")
    logger.log_info(f"Calc took approx {calc_time}")
    response_gauge = Gauge(
        "pi_calc_bench_avg_ping",
        "Average ping response during 4000pi calculation",
        registry=context.prometheusExporter.registry,
    )
    response_gauge.set(calc_average(response_times))


def calc_average(values: list[float]) -> float:
    """Calculate average from list of values.

    Args:
        values: List of values to average.

    Returns:
        Calculated average value.
    """
    sum = 0
    for value in values:
        sum = sum + value
    return sum / len(values)


def get_timestamps(data: str) -> tuple[str, str]:
    """Return start and end timestamps from string data.

    Args:
        data: Input string with timestamp data.

    Returns:
        Start and end timestamps as str.
    """
    split_data = data.split(sep="\n")
    assert len(split_data) == 2, f"Timestamp returned invalid data: {split_data}"
    return split_data[0], split_data[1]


def run_parallel(tasks: list[tuple], timeout: int = 100) -> list[str]:
    """Run submitted tasks in multithreaded executor and collect the results.
    Args:
        tasks: List of tasks written as tuples.
        timeout: Amount of time for executor to wait before terminating the tasks.

    Returns:
        The output of called tasks as list of strings.
    """
    results = []
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(*task) for task in tasks]
        for running_task in running_tasks:
            res = running_task.result(timeout=timeout)
            results.append(res)
    return results


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
        server = client.create_server(
            name=name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network_id}],
            **kwargs,
        )
        client.compute.wait_for_server(server)
    except DuplicateResource as e:
        assert e, "Server already created!"
        server = None
    return server


def create_jumphost(
    client,
    name,
    network_name,
    keypair_name,
    vm_image,
    flavor_name,
    security_groups,
    **kwargs,
):
    """
    Create a jumphost in a specified network.

    Args:
        client (object): The OpenStack client used to interact with the compute and network services.
        name (str): The name of the jumphost to be created.
        network_name (str): The name of the network where the jumphost will be connected.
        keypair_name (str): The name of the keypair to be used for SSH access to the jumphost.
        vm_image (str): The name or ID of the image to be used for the jumphost.
        flavor_name (str): The name or ID of the flavor (hardware configuration) to be used for the jumphost.
        security_groups (list): A list of security group names to apply to the jumphost.
        **kwargs: Additional arguments to be passed to the `create_server` function.

    Returns:
        dict: The jumphost server object if successfully created.

    Raises:
        AssertionError: If any required resource (image, flavor, network, security group) cannot be found or if the jumphost creation fails.

    Example:
        >>> jumphost = create_jumphost(
        ...     client=my_client,
        ...     name="my-jumphost",
        ...     network_name="my-network",
        ...     keypair_name="my-keypair",
        ...     vm_image="ubuntu-20.04",
        ...     flavor_name="m1.small",
        ...     security_groups=["default", "ssh-access"]
        ... )
        >>> print(jumphost["id"])
    """
    keypair_filename = f"{keypair_name}-private"

    image = client.compute.find_image(name_or_id=vm_image)
    assert image, f"Image with name {vm_image} doesn't exist"
    flavor = client.compute.find_flavor(name_or_id=flavor_name)
    assert flavor, f"Flavor with name {flavor_name} doesn't exist"
    network = client.network.find_network(network_name)
    assert network, f"Network with name {network_name} doesn't exist"

    keypair = check_keypair_exists(client, keypair_name=keypair_name)
    if not keypair:
        keypair = client.compute.create_keypair(name=keypair_name)
        assert keypair, f"Keypair with name {keypair_name} doesn't exist"
        with open(keypair_filename, "w") as f:
            f.write("%s" % keypair.private_key)
        os.chmod(keypair_filename, 0o600)

    for security_group in security_groups:
        assert (
            client.network.find_security_group(security_group) is not None
        ), f"Security Group with name {security_group} doesn't exist"

    server = client.create_server(
        name=name,
        image=image.id,
        flavor=flavor.id,
        network=[network.id],
        key_name=keypair.name,
        security_groups=security_groups,
        wait=True,
        auto_ip=False,
        **kwargs,
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
        name_or_id=network
    ), f"Network called {network} not present!"
    return network


def list_networks(client, filter: dict = None) -> list:
    """
    List networks available in the OpenStack environment, optionally filtered by criteria.

    Args:
        client (object): The OpenStack client used to interact with the network service.
        filter (dict, optional): A dictionary of filter criteria to narrow down the list of networks. Default is None.

    Returns:
        list: A list of network objects matching the filter criteria.

    Example:
        >>> networks = list_networks(client=my_client, filter={"status": "ACTIVE"})
        >>> for network in networks:
        ...     print(network["name"])
    """
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
    subnet = client.network.create_subnet(
        name=name, network_id=network_id, ip_version=ip_version, **kwargs
    )
    assert not client.network.find_network(
        name_or_id=subnet
    ), f"Failed to create subnet with name {subnet}"
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


def find_router(client, name_or_id):
    """
    Search router and return it
    @param client: OpenStack client
    @param name_or_id: router name or id
    @return:
    """
    return client.network.find_router(name_or_id=name_or_id)


def add_interface_to_router(client, router, subnet_id):
    """
    Add interface to router
    @param client:
    @param router:
    @param subnet_id:
    @return: Router with changed attributes (id, tenant_id, port_id)
    """
    return client.network.add_interface_to_router(router, subnet_id)


def get_availability_zones(client) -> list:
    """
    Retrieve a list of availability zones from the network service.

    Args:
        client (object): The OpenStack client used to interact with the network service.

    Returns:
        list: A list of availability zone objects.

    Example:
        >>> availability_zones = get_availability_zones(client=my_client)
        >>> for zone in availability_zones:
        ...     print(zone["name"])
    """
    return list(client.network.availability_zones())


def create_lb(client, name, **kwargs):
    """
    Create Loadbalancer and wait until it's in state active
    @param client: OpenStack client
    @param name: lb name
    @param kwargs: additional arguments to be passed to resource create command
    @return created lb
    """
    assert (
        client.load_balancer.create_load_balancer(
            name=name, **kwargs
        ).provisioning_status
        == "PENDING_CREATE"
    ), f"Expected LB {name} not in creation"
    lb = client.load_balancer.wait_for_load_balancer(
        name_or_id=name, status="ACTIVE", failures=["ERROR"], interval=2, wait=300
    )
    assert lb.provisioning_status == "ACTIVE", f"Expected LB {name} not Active"
    assert lb.operating_status == "ONLINE", f"Expected LB {name} not Online"
    return lb


def target_source_calc(jh_name, redirs, logger):
    """
    Calculate and return the target and source IP addresses, port number, and VM name for a specific jump host.

    Args:
        jh_name (str): The name of the jump host.
        redirs (dict): A dictionary containing redirection information, including VMs associated with the jump host.
        logger (object): A logger object used to log information and debug messages.

    Returns:
        tuple: A tuple containing the target IP address (str), source IP address (str), port number (int),
               and VM name (str) of the last VM associated with the specified jump host.
    """
    vm_quantity = len(redirs[jh_name]["vms"])
    target_ip = redirs[jh_name]["addr"]
    pno = redirs[jh_name]["vms"][vm_quantity - 1]["port"]
    source_ip = redirs[jh_name]["vms"][vm_quantity - 1]["addr"]
    vm_name = redirs[jh_name]["vms"][vm_quantity - 1]["vm_name"]
    logger.log_info(
        f"{jh_name}: vm_quantity: {vm_quantity} target_ip: {target_ip} source_ip: {source_ip} pno: {pno}"
    )
    if not source_ip or not target_ip or source_ip == target_ip:
        logger.log_debug(f"IPerf3: {source_ip}<->{target_ip}: skipped")
    return target_ip, source_ip, pno, vm_name
