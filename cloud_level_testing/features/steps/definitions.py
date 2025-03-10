from behave import given, when, then
import openstack
from openstack.cloud._floating_ip import FloatingIPCloudMixin
import time
import random
import string
import subprocess

from libs.ConnectivityClient import SshClient
import os
from cloud_level_testing.features.steps import tools


class StepsDef:
    PING_RETRIES = 60
    collector = tools.Collector()

    @given("I connect to OpenStack")
    def given_i_connect_to_openstack(context):
        cloud_name = context.env.get("CLOUD_NAME")
        context.test_name = context.env.get("TESTS_NAME_IDENTIFICATION")
        context.vm_image = context.env.get("VM_IMAGE")
        context.flavor_name = context.env.get("FLAVOR_NAME")
        context.provider_network_name = context.env.get("PROVIDER_NETWORK_INTERFACE")
        context.client = openstack.connect(cloud=cloud_name)

    @when("A router with name {router_name} exists")
    def router_with_name_exists(context, router_name: str):
        router = context.client.network.find_router(name_or_id=router_name)
        assert router is not None, f"Router with {router_name} doesn't exist"

    @when("A network with name {network_name} exists")
    def connect_to_openstack(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"

    @when("A load balancer with name {lb_name} exists")
    def connect_to_openstack(context, lb_name: str):
        lb = context.client.load_balancer.find_load_balancer(name_or_id=lb_name)
        assert lb is not None, f"Network with {lb_name} doesn't exists"

    @when("A VM with name {vm_name} exists")
    def vm_exists(context, vm_name: str):
        server = context.client.compute.find_server(name_or_id=vm_name)
        assert server, f"VM with name {vm_name} does not exist"
        context.server = server

    @when("A subnet with name {subnet_name} exists in network {network_name}")
    def subnet_with_name_exists_in_network(
        context, subnet_name: str, network_name: str
    ):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with name {network_name} does not exist"
        subnet = context.client.network.find_subnet(name_or_id=subnet_name)
        assert (
            subnet is not None
        ), f"Subnet with name {subnet_name} does not exist in network {network_name}"

    @then("I should be able to list routers")
    def list_routers(context):
        routers = context.client.network.routers()
        assert routers, "Failed to list routers. No routers found."

    @then("I should be able to create {router_quantity:d} routers")
    def create_router(context, router_quantity: int):
        for num in range(1, router_quantity + 1):
            router = tools.create_router(context.client, f"{context.test_name}-{num}")
            context.collector.routers.append(router.id)
            assert (
                router is not None
            ), f"Failed to create router with name {context.test_name}-{num}"
        assert (
            len(context.collector.routers) == router_quantity
        ), f"Failed to create the desired amount of routers"

    @then("I should be able to create port for networks")
    def create_port_for_network(context):
        for network in context.client.network.networks():
            if f"{context.test_name}-network" in network.name:
                port = context.client.network.create_port(network_id=network.id)
                assert port is not None, f"Port creation failed for port {port.id}"
                context.collector.ports.append(port.id)

    @when("A security group with name {security_group_name} exists")
    def security_group_with_name_exists(context, security_group_name: str):
        security_group = context.client.network.find_security_group(
            name_or_id=security_group_name
        )
        assert (
            security_group is not None
        ), f"Security group with name {security_group_name} doesn't exist"

    @when(
        "A security group rule for {security_group_name} with direction {direction} protocol {protocol} and port "
        "range {port_range_min} to {port_range_max} exists"
    )
    def security_group_rule_exists(
        context,
        security_group_name: str,
        direction: str,
        protocol: str,
        port_range_min: int,
        port_range_max: int,
    ):
        security_group = context.client.network.find_security_group(
            name_or_id=security_group_name
        )
        assert (
            security_group
        ), f"Security group with name {security_group_name} does not exist"
        security_group_rules = list(
            context.client.network.security_group_rules(
                security_group_id=security_group.id,
                direction=direction,
                ethertype="IPv4",
                protocol=protocol,
                port_range_min=port_range_min,
                port_range_max=port_range_max,
                remote_ip_prefix="0.0.0.0/0",
            )
        )
        assert len(security_group_rules) > 0, (
            f"No matching security group rule found for {security_group_name}"
            f" with direction {direction}, protocol {protocol},"
            f" and port range {port_range_min} to {port_range_max}"
        )

    @then("I should be able to delete routers")
    def delete_router(context):
        for router_id in context.collector.routers[:]:
            context.client.network.delete_router(router_id)
            time.sleep(2)
            tools.verify_router_deleted(context.client, router_id)
            context.collector.routers.remove(router_id)
        if context.collector.routers:
            for router in context.client.network.routers():
                if context.test_name in router.name:
                    assert (
                        router is not None
                    ), f"Router with name {router.name} doesn't exist"
                    context.client.network.delete_router(router)
                    time.sleep(2)
                    tools.verify_router_deleted(context.client, router.id)
                    if router.id in context.collector.routers:
                        context.collector.routers.remove(router.id)
        assert len(context.collector.routers) == 0, f"Failed to delete routers"

    @then("I should be able to list networks")
    def list_networks(context):
        networks = context.client.network.networks()
        context.logger.log_info(list(network.id for network in networks))
        assert networks, "Failed to list networks. No networks found."

    @then("I should be able to create {network_quantity:d} networks")
    def create_network(context, network_quantity: int):
        for num in range(1, network_quantity + 1):
            network = tools.create_network(
                context.client, name=f"{context.test_name}-network-{num}"
            )
            context.collector.networks.append(network.id)
        assert (
            len(context.collector.networks) == network_quantity
        ), f"Failed to create the desired amount of networks"

    @then(
        "I should be able to create {lb_quantity:d} loadbalancers for {subnet_name} in network {network_name}"
    )
    def create_lb(context, lb_quantity: int, subnet_name: str, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with name {network_name} does not exist"
        subnet = context.client.network.find_subnet(name_or_id=subnet_name)
        assert (
            subnet is not None
        ), f"Subnet with name {subnet_name} does not exist in network {network_name}"
        for num in range(1, lb_quantity + 1):
            lb_name = f"{context.test_name}-loadbalancer-{num}"
            assert (
                context.client.load_balancer.create_load_balancer(
                    name=lb_name, vip_subnet_id=subnet.id
                ).provisioning_status
                == "PENDING_CREATE"
            ), f"Expected LB {lb_name} not in creation"
            lb_return = context.client.load_balancer.wait_for_load_balancer(
                name_or_id=lb_name,
                status="ACTIVE",
                failures=["ERROR"],
                interval=2,
                wait=300,
            )
            context.collector.load_balancers.append(lb_return.id)
            assert (
                lb_return.provisioning_status == "ACTIVE"
            ), f"Expected LB {lb_name} not Active"
            assert (
                lb_return.operating_status == "ONLINE"
            ), f"Expected LB {lb_name} not Online"
        assert (
            len(context.collector.load_balancers) == lb_quantity
        ), f"Failed to create the desired amount of LBs"

    @then("I disable all ports in all networks")
    def disable_all_ports(context):
        context.collector.disabled_ports = []
        for network in context.client.network.networks():
            ports = context.client.network.ports(network_id=network.id)
            for port in ports:
                if port.is_admin_state_up:
                    context.client.network.update_port(port.id, admin_state_up=False)
                    context.collector.disabled_ports.append(port.id)
            for port_id in context.collector.disabled_ports:
                port = context.client.network.get_port(port_id)
                assert (
                    port is not None
                ), f"Port with ID {port_id} not found after update."
                assert (
                    port.is_admin_state_up is False
                ), f"Port with ID {port_id} is not disabled."

    @then("I enable all ports in all networks")
    def enable_all_ports(context):
        context.collector.enabled_ports = []
        for network in context.client.network.networks():
            ports = context.client.network.ports(network_id=network.id)
            for port in ports:
                if not port.is_admin_state_up:
                    context.client.network.update_port(port.id, admin_state_up=True)
                    context.collector.enabled_ports.append(port.id)
            for port_id in context.collector.enabled_ports:
                port = context.client.network.get_port(port_id)
                assert (
                    port is not None
                ), f"Port with ID {port_id} not found after update."
                assert (
                    port.is_admin_state_up is True
                ), f"Port with ID {port_id} is not enabled."

    @then("I should be able to delete a loadbalancer")
    def delete_lb(context):
        lb_list = list(context.client.load_balancer.load_balancers())
        for lb in lb_list:
            if f"{context.test_name}-loadbalancer" in lb.name:
                assert context.client.load_balancer.delete_load_balancer(
                    lb, cascade=True
                ), f"Expected LB {lb} could not be deleted"

    @then("I should be able to delete a networks")
    def delete_network(context):
        for network_id in context.collector.networks[:]:
            context.client.network.delete_network(network_id)
            assert not context.client.network.find_network(
                name_or_id=network_id
            ), f"Network with ID {network_id} already deleted"
            context.collector.networks.remove(network_id)
        if context.collector.networks:
            for network in context.client.network.networks():
                if f"{context.test_name}-network" in network.name:
                    context.client.network.delete_network(network)
                    assert not context.client.network.find_network(
                        name_or_id=network
                    ), f"Network called {network.name} already deleted"
                    if network.id in context.collector.networks:
                        context.collector.networks.remove(network.id)
        assert len(context.collector.networks) == 0, f"Failed to delete networks"

    @then("I should be able to list subnets")
    def list_subnets(context):
        subnets = context.client.network.subnets()
        assert subnets, "Failed to list subnets. No subnets found."

    @then("I am able to delete all the ports")
    def delete_network_ports(context):
        """Delete all ports used in the feature run based on the collector

        Args:
            context: Behave context object
        """
        tools.delete_ports(context)
        assert (
            len(context.collector.ports) == 0
        ), f"failed to delete all ports from all networks under test."

    @then("I should be able to create {subnet_quantity:d} subnets")
    def create_subnet(context, subnet_quantity: int):
        counter_networks = 0
        for network in context.client.network.networks():
            if f"{context.test_name}-network" in network.name:
                context.logger.log_info(f"Creating subnets for network: {network}")
                counter_networks += 1

                cidr = tools.create_subnets(num=subnet_quantity)
                for num in range(1, subnet_quantity + 1):
                    subnet = tools.create_subnet(
                        context.client,
                        f"{context.test_name}-subnet-{num}",
                        network_id=network.id,
                        cidr=cidr[num - 1],
                    )
                    context.logger.log_info(f"Created subnet {subnet.name}")
                    context.collector.subnets.append(subnet.id)

        context.logger.log_info(f"Subnets in collector: {context.collector.subnets}, "
                                f"wished: {subnet_quantity*counter_networks}")
        assert (
            len(context.collector.subnets) == (subnet_quantity * counter_networks)
        ), f"Failed to create the desired amount of subnets"

    @then("I should be able to delete subnets")
    def delete_subnet(context):
        for subnet_id in context.collector.subnets[:]:
            tools.delete_subent_ports(context.client, subnet_id=subnet_id)
            context.client.network.delete_subnet(subnet_id)
            assert not context.client.network.find_subnet(
                name_or_id=subnet_id
            ), f"Subnet with id {subnet_id} was not deleted"
            context.collector.subnets.remove(subnet_id)
        if context.collector.subnets:
            for network in context.client.network.networks():  # list of networks
                for subnet_id in network.subnet_ids:
                    for subnet in context.client.network.subnets():
                        if f"{context.test_name}-subnet" in subnet.name:
                            tools.delete_subent_ports(
                                context.client, subnet_id=subnet_id
                            )
                            subnet = context.client.network.find_subnet(
                                name_or_id=subnet_id
                            )
                            assert subnet, f"Subnet with id {subnet} does not exist"
                            context.client.network.delete_subnet(subnet_id)
                            assert context.client.network.find_subnet(
                                name_or_id=subnet
                            ), f"Subnet with id {subnet} was not deleted"
                            if subnet_id in context.collector.subnets:
                                context.collector.subnets.remove(subnet_id)
        assert len(context.collector.subnets) == 0, f"Failed to delete all subnets"

    @then("I should be able to create {security_group_quantity:d} security groups")
    def create_security_group(context, security_group_quantity: int):
        security_groups = context.client.network.security_groups()
        for num in range(1, security_group_quantity + 1):
            security_group_name = f"{context.test_name}-sg-{num}"
            assert (
                security_group_name not in security_groups
            ), f"security group named: {security_group_name} already exists"
            security_group = context.client.network.create_security_group(
                name=security_group_name,
                description=f"this is the description for security group: {security_group_name}",
            )
            context.collector.security_groups.append(security_group.id)
            assert (
                security_group is not None
            ), f"Security group with name {security_group.name} was not found"
        assert (
            len(context.collector.security_groups) == security_group_quantity
        ), f"Failed to create the desired amount of security groups"

    @then("I should be able to delete a security groups")
    def delete_security_group(context):
        for sec_group_id in context.collector.security_groups[:]:
            context.client.network.delete_security_group(sec_group_id)
            time.sleep(2)
            assert not tools.check_security_group_exists(
                context, sec_group_id
            ), f"Security group with id {sec_group_id} was not deleted"
            context.collector.security_groups.remove(sec_group_id)
        if context.collector.security_groups:
            for sec_group in context.client.network.security_groups():
                security_group = tools.check_security_group_exists(
                    context, sec_group.id
                )
                assert (
                    security_group
                ), f"Security group with name {sec_group.name} does not exist"
                if f"{context.test_name}-sg" in sec_group.name:
                    context.client.network.delete_security_group(sec_group.id)
                    time.sleep(2)
                    assert not tools.check_security_group_exists(
                        context, sec_group.id
                    ), f"Security group with name {sec_group.name} was not deleted"
                    if sec_group.id in context.collector.security_groups:
                        context.collector.security_groups.remove(sec_group.id)
        assert (
            len(context.collector.security_groups) == 0
        ), f"Failed to delete security groups"

    @then(
        "I should be able to create {security_group_rules_quantity:d} security group rules"
    )
    def create_security_group_rules(context, security_group_rules_quantity: int):
        sec_groups = list(context.client.network.security_groups())
        base_port = 80
        for num in range(1, security_group_rules_quantity + 1):
            port_range_min = base_port + num - 1
            port_range_max = port_range_min
            for sec_group in sec_groups:
                if context.test_name in sec_group.name:
                    sel_sec_group = tools.check_security_group_exists(
                        context, sec_group.name
                    )
                    sel_sec_group_rules = [
                        rule
                        for rule in context.client.network.security_group_rules(
                            direction="ingress",
                            protocol="tcp",
                            port_range_min=port_range_min,
                            port_range_max=port_range_max,
                        )
                        if rule.security_group_id == sel_sec_group.id
                    ]
                    assert (
                        len(sel_sec_group_rules) == 0
                    ), "There are already security group rules for the selected groups"

                    new_security_group_rule = (
                        context.client.network.create_security_group_rule(
                            security_group_id=sel_sec_group.id,
                            direction="ingress",
                            ethertype="IPv4",
                            protocol="tcp",
                            port_range_min=port_range_min,
                            port_range_max=port_range_max,
                            remote_ip_prefix="0.0.0.0/0",
                        )
                    )
                    context.collector.security_groups_rules.append(
                        new_security_group_rule.id
                    )

            assert len(sec_groups) > 0, "There are no security groups"
        assert len(context.collector.security_groups_rules) == int(
            security_group_rules_quantity
        ), f"Failed to create the desired amount of security group rules"

    @then("I should be able to delete a security group rules")
    def delete_security_group_rules(
        context,
    ):
        for sec_group_rule_id in context.collector.security_groups_rules[:]:
            context.client.network.delete_security_group_rule(sec_group_rule_id)
            context.collector.security_groups_rules.remove(sec_group_rule_id)
        if context.collector.security_groups_rules:
            sec_groups = list(context.client.network.security_groups())
            for sec_group in sec_groups:
                if context.test_name in sec_group.name:
                    sel_sec_group = tools.check_security_group_exists(
                        context, sec_group.name
                    )
                    sel_sec_group_rules = []
                    for rule in context.client.network.security_group_rules():
                        if rule.security_group_id == sel_sec_group.id:
                            sel_sec_group_rules.append(rule)
                            context.client.network.delete_security_group_rule(rule.id)
                            if rule.id in context.collector.security_groups_rules:
                                context.collector.security_groups_rules.remove(rule.id)
                    assert (
                        len(sel_sec_group_rules) > 0
                    ), "There are no security group rules for the selected groups"
            assert len(sec_groups) > 0, "There are no security groups"
        assert (
            len(context.collector.security_groups_rules) == 0
        ), f"Failed to delete security groups rules"

    @then("I should be able to create availability zone named {availability zone}")
    def create_availability_zone(context, availability_zone_name):
        availability_zones = context.compute.availability_zones()
        for zone in availability_zones:
            if zone.name == availability_zone_name:
                return f"Availability zone {availability_zone_name} already exist"
        context.compute.create_availability_zone(name=availability_zone_name)

    @then("I should be able to delete an availability zone named {availability_zone}")
    def delete_availability_zone(context, name):
        availability_zones = context.compute.availability_zones()
        for zone in availability_zones:
            if zone.name == name:
                context.compute.delete_availability_zone(name=zone.name)

    @then(
        "Then I should be able to create a plain floating ip which is not associated to something"
    )
    def create_floating_ip_plain(
        context,
        wait=False,
        timeout=60,
    ):
        ip = FloatingIPCloudMixin.create_floating_ip(
            network=context.provider_network_name,
            wait=wait,
            timeout=timeout,
        )
        floating_ip = FloatingIPCloudMixin.get_floating_ip(ip.id)
        context.collector.plain_floating_ips.append(floating_ip.id)
        assert floating_ip is None, f"plain floating ip was not created"

    @then(
        "I should be able to create a floating ip on {subnet}, on {server}, with {fixed_address}, for {nat_destination}"
        "on {port}"
    )
    def create_floating_ip(
        context,
        subnet=None,
        server=None,
        fixed_address=None,
        nat_destination=None,
        port=None,
        wait=False,
        timeout=60,
    ):
        ip = FloatingIPCloudMixin.create_floating_ip(
            network=subnet,
            server=server,
            fixed_address=fixed_address,
            nat_destination=nat_destination,
            port=port,
            wait=wait,
            timeout=timeout,
        )
        floating_ip = FloatingIPCloudMixin.get_floating_ip(ip.id)
        context.collector.floating_ips.append(floating_ip.id)
        assert floating_ip is None, f"floating ip was not created"

    @then("I should be able to delete floating ip with id: {floating_ip_id}")
    def delete_floating_ip(context, floating_ip_id):
        for ip_id in context.collector.floating_ips[:]:
            FloatingIPCloudMixin.delete_floating_ip(floating_ip_id=ip_id)
            floating_ip = FloatingIPCloudMixin.get_floating_ip(ip_id)
            assert (
                floating_ip is not None
            ), f"floating ip with id {ip_id} was not deleted"
            context.collector.floating_ips.remove(ip_id)
        assert (
            len(context.collector.floating_ips) == 0
        ), f"Failed to delete floating IPs"

    @then("I should be able to delete all previously plain floating ips")
    def delete_all_plain_floating_ip(context):
        for ip_id in context.collector.plain_floating_ips[:]:
            FloatingIPCloudMixin.delete_floating_ip(floating_ip_id=ip_id)
            floating_ip = FloatingIPCloudMixin.get_floating_ip(ip_id)
            context.logger.log_info(f"Deleting plain floating ip with {ip_id}")
            assert (
                    floating_ip is not None
            ), f"floating ip with id {ip_id} was not deleted"
            context.collector.floating_ips.remove(ip_id)
        assert (
                len(context.collector.floating_ips) == 0
        ), f"Failed to delete floating IPs"

    @then("I should be able to create {vms_quantity:d} VMs")
    def create_vm(context, vms_quantity: int):
        # config
        security_groups = ["default", "ping-sg"]
        user_data = f"""#cloud-config
        packages:
        - iperf3
        - jq
        """
        network_count = 0
        for network in context.client.network.networks():
            if context.test_name in network.name:
                for num in range(1, vms_quantity + 1):
                    vm_name = f"{context.test_name}-vm-{''.join(random.choices(string.ascii_letters + string.digits, k=10))}"
                    server = tools.create_vm(
                        context.client,
                        vm_name,
                        context.vm_image,
                        context.flavor_name,
                        network.id,
                        security_groups=security_groups,
                        userdata=user_data,
                    )
                    time.sleep(5)
                    context.collector.virtual_machines.append(server)
                    created_server = context.client.compute.find_server(
                        name_or_id=vm_name
                    )
                    # context.collector.virtual_machines.append(created_server.ip)
                    assert (
                        created_server
                    ), f"VM with name {vm_name} was not created successfully"
        # TODO rework check to compare with collector eg. len(context.collector.networks)
        assert (
            len(context.collector.virtual_machines) == vms_quantity * network_count
        ), f"Failed to create the desired amount of VMs"

    @then("I should be able to delete the VMs")
    def delete_vm(context):
        vms = (
            context.collector.virtual_machines
            if len(context.collector.virtual_machines)
            else list()
        )
        for vm in context.client.compute.servers():
            if vm.id in vms or context.test_name in vm.name:
                context.client.compute.delete_server(vm.id)
                context.client.compute.wait_for_delete(vm)
                deleted_server = context.client.compute.find_server(name_or_id=vm.id)
                assert (
                    deleted_server
                ), f"VM with name {vm.name} was not deleted successfully"
                if vm.id in context.collector.virtual_machines:
                    context.collector.virtual_machines.remove(vm.id)
        assert len(context.collector.virtual_machines) == 0, f"Failed to delete VMs"

    @then("I create {quantity_volumes:d} volumes")
    def create_multiple_volumes(context, quantity_volumes: int):
        context.volumes = []
        for num in range(1, quantity_volumes + 1):
            volume_name = f"{context.test_name}-volume-{num}"
            volume = context.client.block_store.create_volume(size=10, name=volume_name)
            context.collector.volumes.append(volume.id)
            context.volumes.append(volume)
            tools.ensure_volume_exist(
                client=context.client,
                volume_name=volume_name,
                test_name=context.test_name,
            )
        assert (
            len(context.collector.volumes) == quantity_volumes
        ), f"Failed to create the desired amount of volumes"

    @then("I delete all volumes from test")
    def delete_all_volumes(context):
        for volume_id in context.collector.volumes[:]:
            context.client.block_store.delete_volume(volume_id, ignore_missing=True)
            time.sleep(2)
            tools.verify_volume_deleted(context.client, volume_id=volume_id)
            context.collector.volumes.remove(volume_id)
        if context.collector.volumes:
            volumes = list(context.client.block_store.volumes())
            for volume in volumes:
                if f"{context.test_name}-volume" in volume.name:
                    context.client.block_store.delete_volume(
                        volume, ignore_missing=True
                    )
                    time.sleep(2)
                    tools.verify_volume_deleted(context.client, volume_id=volume.id)
                    if volume.id in context.collector.volumes:
                        context.collector.volumes.remove(volume.id)
            assert filter(
                lambda alist: f"{context.test_name}" not in alist,
                list(context.client.block_store.volumes()),
            )
        tools.verify_volumes_deleted(context.client, context.test_name)
        assert len(context.collector.volumes) == 0, f"Failed to delete volumes"

    @then(
        "I create a jumphost with name {jumphost_name} on network {network_name} with keypair {keypair_name}"
    )
    def create_a_jumphost(
        context, jumphost_name: str, network_name: str, keypair_name: str
    ):
        """Create a jumphost server in openstack.

        Args:
            context: Behave context object.
            jumphost_name: Name of created jumphost.
            network_name: Name of network where jumphost should be connected.
            keypair_name: Name of access keypair to use, creates new one if it doesn't exist.
        """
        # config
        ping_sec_group_name = "ping-sg"
        ping_sec_group_description = "Ping security group - allow ICMP"
        security_groups = ["ssh", "default", ping_sec_group_name]
        keypair_filename = f"{keypair_name}-private"
        user_data = f"""#cloud-config
        packages:
        - iperf3
        - jq
        runcmd:
        - iperf3 -Ds
        """
        keypair = tools.check_keypair_exists(context.client, keypair_name=keypair_name)
        if not keypair:
            keypair = context.client.compute.create_keypair(name=keypair_name)
            assert keypair, f"Keypair with name {keypair_name} doesn't exist"
            with open(keypair_filename, "w") as f:
                f.write("%s" % keypair.private_key)
            os.chmod(keypair_filename, 0o600)
        ping_sec_group = tools.check_security_group_exists(
            context, sec_group_name=ping_sec_group_name
        )
        if not ping_sec_group:
            context.logger.log_info(f"SG not found, creating")
            ping_sec_group = tools.create_security_group(
                context, ping_sec_group_name, ping_sec_group_description
            )
            tools.create_security_group_rule(
                context, ping_sec_group.id, protocol="icmp"
            )

        for security_group in security_groups:
            assert (
                tools.check_security_group_exists(context, security_group) is not None
            ), f"Security Group with name {security_group} doesn't exist"

        server = tools.create_jumphost(
            context.client,
            jumphost_name,
            network_name,
            keypair_name,
            context.vm_image,
            context.flavor_name,
            security_groups=security_groups,
            availability_zone="nova",
            userdata=user_data,
        )
        context.collector.jumphosts.append(server.id)

    @given("I have deployed a VM with IP {vm_ip_address}")
    def initialize(context, vm_ip_address: str):
        context.fip_address = vm_ip_address

    @given("I have a private key at {keypair_name} for {username}")
    def check_private_key_exists(context, keypair_name: str, username: str):
        """Check if private key exists on host, if not, create new keypair in openstack and save its private key on host.

        Args:
            context: Behave context object.
            keypair_name: Name of keypair to use/create.
            username: Username associated with the keypair.
        """
        context.vm_private_ssh_key_path = f"{keypair_name}-private"
        context.vm_username = username
        if not os.path.isfile(context.vm_private_ssh_key_path):
            context.logger.log_info(f"Private key not found, creating new one")
            if context.client.get_keypair(name_or_id=keypair_name):
                assert context.client.delete_keypair(
                    name=keypair_name
                ), f"Failed to delete the old keypair {keypair_name}."
            keypair = context.client.compute.create_keypair(name=keypair_name)
            assert keypair, f"Keypair with name {keypair_name} doesn't exist"
            with open(f"{keypair_name}-private", "w") as f:
                f.write("%s" % keypair.private_key)
            os.chmod(f"{keypair_name}-private", 0o600)
        context.keypair_name = keypair_name

    @then("I should be able to SSH into JHs and test their {conn_test} connectivity")
    def step_iterate_steps(context, conn_test: str):
        context.assertline = None
        context.logger.log_info(f"jh on {context.jh[0]}")
        jh_quantity = len(context.jh)
        for i in range(0, jh_quantity):
            if not isinstance(context.jh, str):
                context.fip_address = context.jh[i]
                context.execute_steps(
                    f"""
                    Then I should be able to SSH into the VM
                    Then I should be able to collect all network IPs
                    And be able to ping all IPs to test {conn_test} connectivity
                    """
                )
            else:
                context.assertline = f"No matching Jumphosts was found"
        assert context.assertline is None, context.assertline

    @then(
        "I should be able to retrieve the first floating ip and portnumber of the network"
    )
    def get_jh_fip(context):
        context.fip_address = context.jh[0]
        assert context.fip_address, "jh has no valid fip"
        try:
            context.pno = context.redirs[f"{context.test_name}jh{0}"]["vms"][1]["port"]
        except:
            context.logger.log_info("no portnumber found")

    @then("I should be able to SSH into the VM")
    def test_ssh_connection(context):
        context.logger.log_info(
            f"key: {context.keypair_name} {context.vm_private_ssh_key_path}"
        )
        if hasattr(context, "pno"):
            context.logger.log_info(
                f"ssh through portforwarding: {context.fip_address}/{context.pno}"
            )
            attempts = 20
            context.ssh_client = SshClient(
                context.fip_address,
                context.vm_username,
                context.vm_private_ssh_key_path,
                context.logger,
                context.pno,
            )
        else:
            context.logger.log_info(f"ssh into: {context.fip_address}")
            attempts = 10
            context.ssh_client = SshClient(
                context.fip_address,
                context.vm_username,
                context.vm_private_ssh_key_path,
                context.logger,
            )
        if not context.ssh_client:
            context.assertline = f"could not access VM {context.fip_address}"

        if context.ssh_client.check_server_readiness(attempts=attempts):
            context.logger.log_info(f"Server ready for SSH connections")
        else:
            context.logger.log_info(f"Server SSH connection failed to establish")
        context.ssh_client.print_working_directory()

    @then("be able to communicate with the internet")
    def test_internet_connectivity(context):
        context.ssh_client.test_internet_connectivity()

    @then("I should be able to collect all network IPs")
    def collect_network_ips(context):
        assert hasattr(
            context, "redirs"
        ), f"No redirs found infrastructure not completely built yet"
        assert isinstance(context.redirs, dict), f"redirs is no dictionary, but is {type(context.redirs)}"
        context.ips, assertline = tools.collect_ips(
            context.redirs, context.test_name, context.logger
        )
        if assertline != None:
            context.assertline = assertline

    @given("I have deployed JHs")
    def ensure_jh_deployed(context):
        assert hasattr(
            context, "redirs"
        ), f"No redirs found infrastructure not completely built yet"
        context.logger.log_debug(f"vm data {context.redirs}")
        assert isinstance(context.redirs, dict), f"redirs is no dictionary, but is {type(context.redirs)}"
        context.jh = tools.collect_jhs(
            context.redirs, context.test_name, context.logger
        )
        assert len(context.jh) > 0, f"no jh found for {context.test_name}"

    @then("I should be able to SSH into VMs and perform {conn_test} test")
    def substeps(context, conn_test):
        context.assertline = None
        jh_quantity = len(context.jh)
        context.logger.log_info(f"{jh_quantity} jump hosts and iterations")
        for i in range(0, jh_quantity):
            jh_name = f"{context.test_name}jh{i}"
            target_ip, source_ip, pno, vm_name = tools.target_source_calc(
                jh_name, context.redirs, context.logger
            )
            context.fip_address = context.jh[i]
            context.pno = pno
            context.logger.log_info(
                f"target {target_ip}, source {source_ip} fip {context.fip_address}/{context.pno}"
            )
            context.execute_steps(
                """
                Then I should be able to SSH into the VM
                Then I should sleep for 10 seconds
                """
            )
            target_name = jh_name
            source_name = vm_name
            context.assertline = context.ssh_client.run_iperf_test(
                conn_test,
                context.test_name,
                context.fip_address,
                target_ip,
                target_name,
                source_ip,
                source_name,
            )
        assert context.assertline == None, context.assertline

    @then("be able to ping all IPs to test {conn_test} connectivity")
    def ping_ips_test(context, conn_test: str):
        tot_ips = len(context.ips)
        if len(context.ips) > 0:
            for ip in context.ips:
                result, assertline = context.ssh_client.test_internet_connectivity(
                    conn_test, ip, tot_ips
                )
            if result[1] != 0:
                context.assertline = assertline

    @then("be able to communicate with {ip} to test {conn_test} connectivity")
    def test_domain_connectivity(context, ip: str, conn_test: str):
        result, assertline = context.ssh_client.test_internet_connectivity(
            conn_test, ip
        )
        assert result[1] == 0, assertline

    @then("close the connection")
    def close_connection(context):
        context.ssh_client.close_conn()

    @then("I attach a floating ip to server {server_name}")
    def attach_floating_ip_to_server(context, server_name: str):
        """Create new floating IP and attach it to the server.
        Args:
            context: Behave context object.
            server_name: Name of the server for floating IP.
        """
        fip = tools.attach_floating_ip_to_server(context, server_name)
        assert fip is not None

    @then(
        "I start calculating 4000 digits of pi on VM and check the ping response"
    )
    def calculate_pi_on_vm(context):
        """Behave step for calculating average ping response of a machine under load, created by calculating 4000 digits of pi.

        Args:
            context: Behave context object.
        """
        calc_command = "date +%s && time echo 'scale=4000; 4*a(1)' | bc -l >/dev/null 2>&1 && date +%s"
        ping_parse_magic = (
            "| tail -n +2 | head -n -4 |awk '{split($0,a,\" \"); print a[1], a[8]}'"
        )
        ping_command = f"ping -D -c{StepsDef.PING_RETRIES} {context.fip_address} {ping_parse_magic}"

        ping_server_ssh_client = SshClient(
            context.fip_address,
            context.vm_username,
            context.vm_private_ssh_key_path,
            context.logger,
        )
        ping_server_ssh_client.connect()

        try:
            tasks = [
                (context.ssh_client.execute_command, calc_command, True),
                (ping_server_ssh_client.execute_command, ping_command),
            ]
            results = tools.run_parallel(tasks)
            tools.parse_ping_output(context, results, context.logger)
        except Exception as e:
            context.logger.log_info(f"Task failed with exception: {e}")
        ping_server_ssh_client.close_conn()
        context.ssh_client.close_conn()

    @given("I can get the shared context from previous feature")
    def step_given_use_value_from_first_feature(context):
        context.test_name = context.shared_context.test_name
        context.redirs = context.shared_context.redirs
        context.keypair_name = context.shared_context.keypair_name
        assert hasattr(context, "redirs"), "did not get context"

    @given("I have deployed jumphosts with floating ips")
    def get_deployed_jumphosts(context):
        """Find all jumphosts and get their respective floating ips. Jumphost servers are expected to contain 'jh' substring in their name.
        Args:
            context: Behave context object.
        """
        context.jh_floating_ips = []
        servers = context.client.compute.servers()
        for server in servers:
            if "jh" in server.name.lower():
                for network_name, network_info in server.addresses.items():
                    for address in network_info:
                        if address["OS-EXT-IPS:type"] == "floating":
                            context.jh_floating_ips.append(address["addr"])
        assert (
            context.jh_floating_ips
        ), f"No jumphosts with attached floating ip address"

    @then("I should be able to ping the jumphosts with floating ips")
    def ping_jumphosts_fip(context) -> tuple[dict, int]:
        """Try to ping all jumphosts on their floating ip, collect ping response duration and failure count.
        Args:
            context: Behave context object.
        Returns:
            Pair of ping results dictionary (ip_address : ping response time) and ping failure counter.
        """
        ping_failure_count = 0
        ping_results = {}
        for address in context.jh_floating_ips:
            start_time = time.time()
            result = subprocess.run(
                ["ping", "-c", "1", address],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            end_time = time.time()
            duration = end_time - start_time
            if result.returncode != 0:
                ping_failure_count += 1
                context.logger.log_error(f"Ping for ip {address} failed.")
            else:
                context.logger.log_info(
                    f"Ping for ip {address} took {duration:.2f} seconds."
                )
                ping_results[address] = duration

        context.logger.log_info(f"Ping check results: {ping_results}")
        return ping_results, ping_failure_count

    @then("I should sleep for {slseconds:d} seconds")
    def sleep_temp(context, slseconds):
        context.logger.log_info(f"sleeping {slseconds}s")
        time.sleep(slseconds)
