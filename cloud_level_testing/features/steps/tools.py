import ipaddress
import time
import datetime
from functools import wraps
from libs.loggerClass import Logger
from concurrent.futures import ThreadPoolExecutor
import os

import yaml
from openstack.exceptions import DuplicateResource
import openstack


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
        router = create_router(self.client, name, **kwargs)
        self.routers.append(router.id)
        return router

    def create_network(self, name, **kwargs):
        net = create_network(self.client, name, **kwargs)
        self.networks.append(net.id)
        return net

    def create_subnet(self, name, network_id, ip_version=4, **kwargs):
        subnet = create_subnet(self.client, name, network_id, ip_version, **kwargs)
        self.subnets.append(subnet.id)
        return subnet

    def add_interface_to_router(self, router, subnet_id):
        router_update = add_interface_to_router(self.client, router, subnet_id)
        self.router_subnets.append({"router": router.id, "subnet": subnet_id})
        return router_update

    def find_router(self, name_or_id):
        return find_router(self.client, name_or_id)

    def find_server(self, name_or_id):
        return self.client.compute.find_server(name_or_id=name_or_id)

    def delete_router_subnets(self):
        for router_subnet in self.router_subnets:
            router = router_subnet["router"]
            subnet_id = router_subnet["subnet"]
            res = self.client.network.remove_interface_from_router(router, subnet_id)
            if not res:
                # success
                self.router_subnets.remove({"router": router.id, "subnet": subnet_id})

    def delete_security_groups(self):
        for security_group in self.security_groups:
            self.client.network.delete_security_group(security_group)
            self.security_groups.remove(security_group)

    def create_jumphost(self, name, network_name, keypair_name, vm_image, flavor_name,
                        security_groups, **kwargs):
        vm = create_jumphost(self.client, name, network_name, keypair_name, vm_image, flavor_name,
                             security_groups, **kwargs)
        self.virtual_machines.append(vm.id)
        return vm

    def create_floating_ip(self, server_name):
        fip = create_floating_ip(self.client, server_name)
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
            name=sec_group_name,
            description=description
        )
        self.security_groups.append(security_group.id)
        assert security_group is not None, f"Security group with name {security_group.name} was not found"
        return security_group

    def create_security_group_rule(self, sec_group_id: str, protocol: str,
                                   port_range_min: int = None, port_range_max: int = None,
                                   direction: str = 'ingress', remote_ip_prefix: str = '0.0.0.0/0'):

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
        assert sec_group_rule is not None, f"Rule for security group {sec_group_id} was not created"
        return sec_group_rule


class Tools:

    @staticmethod
    def load_env_from_yaml():
        with open("./env.yaml", "r+") as file:
            env = yaml.safe_load(file)
        return env

    @staticmethod
    def env_is_true(value):

        if value is None:
            return False
        elif isinstance(value, bool):
            return value
        # If the value is a string, check if it is 'True' (case-insensitive)
        elif isinstance(value, str):
            return value.lower() == "true"
        # Otherwise, default to False
        else:
            return False


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"time taken by {func.__name__} is {end - start}")
        return result, end - start

    return wrapper


def add_value_to_dict_list(d, key, value):
    if key not in d:
        d[key] = []
    d[key] = value


def create_subnets(num):
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
    Iterate addresses of server object and return first floating ip we find.
    Typical types are 'floating' or 'fixed'.
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
    if check_volumes_created(client=client, test_name=test_name) == "available":
        volumes = list(client.block_store.volumes(name=volume_name))
        if not volumes:
            volume = client.block_store.create_volume(size=size, name=volume_name)
            client.block_store.wait_for_status(
                volume, "available", interval=interval, wait=wait
            )


def verify_volumes_deleted(client, test_name):
    volumes_test = [
        volume
        for volume in client.block_store.volumes()
        if f"{test_name}-volume" in volume.name
    ]
    assert len(volumes_test) == 0, "Some volumes still exist"


def verify_volume_deleted(client, volume_id):
    assert not client.block_store.find_volume(
        name_or_id=volume_id
    ), f"Volume with ID {volume_id} was not deleted"


def verify_router_deleted(client, router_id):
    assert not client.network.find_router(
        name_or_id=router_id
    ), f"Router with ID {router_id} was not deleted"


def check_volumes_created(client, test_name):
    for volume in client.volume.volumes():
        if test_name in volume.name:
            volume = client.block_store.wait_for_status(
                volume, "available", interval=2, wait=120
            )
            assert volume.status == "available", f"Volume {volume.name} not available"
            return volume.status


def collect_float_ips(client, logger: Logger):
    ips = []
    assertline = None
    floating_ips = client.network.ips()
    for ip in floating_ips:
        ips.append(ip.floating_ip_address)
        logger.log_debug(f"found floating ip {ip.floating_ip_address}")
    if len(ips) == 0:
        assertline = f"No ips found"
    return ips, assertline


def collect_jhs(client, test_name, logger: Logger):
    servers = client.compute.servers()
    lookup = f"{test_name}-jh"
    jhs = []
    jh = None
    for name in servers:
        logger.log_debug(f"found host {name.name}")
        if lookup in name.name:
            logger.log_debug(f"String containing '{lookup}': {name.name}")
            jh = client.compute.find_server(name_or_id=name.name)
            assert jh, f"No Jumphosts with {lookup} in name found"
            if jh:
                for key in jh.addresses:
                    if test_name in key:
                        logger.log_debug(f"String containing '{test_name}': {key}")
                        jhs.append(
                            {"name": name.name, "ip": jh.addresses[key][1]["addr"]}
                        )
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
    script_path = f'{testname}-wait'
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
        with open(script_path, 'w') as file:
            file.write(script_content)
        os.chmod(script_path, 0o755)
    except:
        assertline = f"Failed to write script file {script_path}"
    return assertline


def delete_wait_script(testname):
    assertline = None
    script_path = f'{testname}-wait'
    try:
        os.remove(script_path)
        print("\b")
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


def parse_ping_output(data: list[str], logger: Logger):
    """Parse the outputs of the ping response test and print them to logger.

    Args:
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
            **kwargs
        )
        client.compute.wait_for_server(server)
    except DuplicateResource as e:
        assert e, "Server already created!"
        server = None
    return server


def create_jumphost(client, name, network_name, keypair_name, vm_image, flavor_name, security_groups, **kwargs):
    # config
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
        with open(keypair_filename, 'w') as f:
            f.write("%s" % keypair.private_key)
        os.chmod(keypair_filename, 0o600)

    for security_group in security_groups:
        security_group = client.network.find_security_group(security_group)
        assert security_group, f"Security Group with name {security_group} doesn't exist"

    server = client.create_server(
        name=name,
        image=image.id,
        flavor=flavor.id,
        network=[network.id],
        key_name=keypair.name,
        security_groups=security_groups,
        wait=True,
        auto_ip=False,
        **kwargs
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


def list_networks(client, filter: dict = None) -> list:
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
    subnet = client.network.create_subnet(name=name,
                                          network_id=network_id,
                                          ip_version=ip_version,
                                          **kwargs)
    time.sleep(5)
    assert not client.network.find_network(name_or_id=subnet), \
        f"Failed to create subnet with name {subnet}"
    return subnet


def create_floating_ip(client, server_name):
    server = client.compute.find_server(name_or_id=server_name)
    assert server, f"Server with name {server_name} not found"
    return client.add_auto_ip(server=server, wait=True)


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
    return list(client.network.availability_zones())


def create_lb(client, name, **kwargs):
    """
    Create Loadbalancer and wait until it's in state active
    @param client: OpenStack client
    @param name: lb name
    @param kwargs: additional arguments to be passed to resource create command
    @return created lb
    """
    assert (client.load_balancer.create_load_balancer(name=name, **kwargs).
            provisioning_status == "PENDING_CREATE"), f"Expected LB {name} not in creation"
    lb = client.load_balancer.wait_for_load_balancer(name_or_id=name,
                                                     status='ACTIVE',
                                                     failures=['ERROR'], interval=2,
                                                     wait=300)
    assert lb.provisioning_status == "ACTIVE", f"Expected LB {name} not Active"
    assert lb.operating_status == "ONLINE", f"Expected LB {name} not Online"
    return lb


def target_source_calc(jh_name, redirs, logger):
    vm_quantity = len(redirs[jh_name]['vms'])
    target_ip = redirs[jh_name]['addr']
    source_ip = redirs[jh_name]['fip']
    pno = redirs[jh_name]['vms'][vm_quantity - 1]['port']
    logger.log_debug(f"{jh_name}: vm_quantity: {vm_quantity} target_ip: {target_ip} source_ip: {source_ip} pno: {pno}")
    if not source_ip or not target_ip or source_ip == target_ip:
        logger.log_debug(f"IPerf3: {source_ip}<->{target_ip}: skipped")
    return target_ip, source_ip, pno
