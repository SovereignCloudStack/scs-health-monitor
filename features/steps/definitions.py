from behave import given, when, then
import openstack
from openstack.cloud._floating_ip import FloatingIPCloudMixin


class StepsDef:

    @given("I connect to OpenStack")
    def given_i_connect_to_openstack(context):
        cloud_name = context.env.get("CLOUD_NAME", "gx")
        context.client = openstack.connect(cloud=cloud_name)

    @when("A router with name {router_name} exists")
    def when_a_router_with_name_exists(context, router_name: str):
        router = context.client.network.find_router(name_or_id=router_name)
        assert router is not None, f"Router with {router_name} doesn't exist"

    @when("A network with name {network_name} exists")
    def when_i_connect_to_openstack(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"

    @when('A VM with name {vm_name} exists')
    def vm_exists(context, vm_name: str):
        server = context.client.compute.find_server(name_or_id=vm_name)
        assert server, f"VM with name {vm_name} does not exist"
        context.server = server

    @when("A subnet with name {subnet_name} exists in network {network_name}")
    def when_a_subnet_with_name_exists_in_network(
        context, subnet_name: str, network_name: str
    ):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with name {network_name} does not exist"
        subnet = context.client.network.find_subnet(name_or_id=subnet_name)
        assert (
            subnet is not None
        ), f"Subnet with name {subnet_name} does not exist in network {network_name}"

    @then("I should be able to list routers")
    def then_i_should_be_able_to_list_routers(context):
        routers = context.client.network.routers()
        assert routers, "Failed to list routers. No routers found."

    @then("I should be able to create a router with name {router_name}")
    def create_a_router(context, router_name: str):
        router = context.client.network.find_router(name_or_id=router_name)
        assert router is None, f"Router with name {router_name} already exist"
        router = context.client.network.create_router(name=router_name)
        assert router is not None, f"Failed to create router with name {router_name}"

    @when("A security group with name {security_group_name} exists")
    def when_a_security_group_with_name_exists(context, security_group_name: str):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert  security_group is not None, f"Security group with name {security_group_name} doesn't exist"

    @when("A security group rule for {security_group_name} with direction {direction} protocol {protocol} and port range {port_range_min} to {port_range_max} exists")
    def create_security_group_rule(context, security_group_name:str, direction:str, protocol:str, port_range_min:int,
                                   port_range_max:int):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group, f"Security group with name {security_group_name} does not exist"
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

    @then("I should be able to delete a router with name {router_name}")
    def delete_a_router(context, router_name: str):
        router = context.client.network.find_router(name_or_id=router_name)
        assert router is not None, f"Router with name {router_name} doesn't exist"
        context.client.network.delete_router(router)
        assert not context.client.network.find_router(
            name_or_id=router_name
        ), f"Router with name {router_name} was not deleted"

    @then("I should be able to list networks")
    def list_networks(context):
        networks = context.client.network.networks()
        assert networks, "Failed to list networks. No networks found."

    @then("I should be able to create a network with name {network_name}")
    def create_a_network(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is None, f"Network with {network_name} already exists"
        network = context.client.network.create_network(name=network_name)
        assert not context.client.network.find_network(
            name_or_id=network), f"Network called {network} created"

    @then("I should be able to create a security group with name {security_group_name} with {description}")
    def create_a_security_group(context, security_group_name: str, description: str):
        security_groups = context.client.network.security_groups()
        assert security_group_name not in security_groups, f"security group named: {security_group_name} already exists"
        security_group = context.client.network.create_security_group(
            name=security_group_name, description=description
        )
        assert security_group is not None, f"Security group with name {security_group.name} was not found"

    @then("I should be able to delete a network with name {network_name}")
    def delete_a_network(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"
        context.client.network.delete_network(network)
        assert not context.client.network.find_network(
            name_or_id=network
        ), f"Network called {network_name} already deleted"

    @then("I should be able to create a jumphost with name {jumphost_name}")
    def create_a_jumphost(context, jumphost_name: str):
        server = context.client.network.find_network(name_or_id=jumphost_name)
        assert server is None, f"Jumphost with {jumphost_name} already exists"
        context.client.compute.create_server(name=jumphost_name)
        context.client.network.delete_network(server)
        assert context.client.network.find_network(name_or_id=server), f"Jumphost called {jumphost_name} created"

    @then("I should be able to list subnets")
    def list_subnets(context):
        subnets = context.client.network.subnets()
        assert subnets, "Failed to list subnets. No subnets found."

    @then('I should be able to create a subnet with name {subnet_name} in network {network_name} with {cidr}')
    def create_a_subnet(context, subnet_name: str, network_name: str, cidr):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with name {network_name} does not exist"
        subnet = context.client.network.create_subnet(name=subnet_name, network_id=network.id, ip_version=4,
                                                      cidr=cidr)
        assert not context.client.network.find_network(name_or_id=subnet), f"Failed to create subnet with name {subnet}"

    @then("I should be able to delete a subnet with name {subnet_name}")
    def delete_a_subnet(context, subnet_name: str):
        subnet = context.client.network.find_subnet(name_or_id=subnet_name)
        assert subnet is not None, f"Subnet with name {subnet_name} does not exist"
        context.client.network.delete_subnet(subnet.id)
        assert not context.client.network.find_subnet(name_or_id=subnet_name), f"Subnet with name {subnet_name} was not deleted"

    @then("I should be able to create a security group <security_group> with {description}")
    def create_a_security_group(context, security_group_name: str, desc: str):
        security_groups = context.network.security_groups()
        assert security_group_name not in security_groups, f"security group named: {security_group_name} already exists"
        security_group = context.network.create_security_group(
            name=security_group_name, description=desc
        )
        assert (
            security_group is not None
        ), f"Security group with name {security_group.name} was not found"

    @then("I should be able to create security group rule {rule}")
    def create_security_rule(context, security_group, port_range_min: int, port_range_max: int,
                                                      direction: str ='ingress', remote_ip_prefix='0.0.0.0/0',
                                                      ethertype:str ='IPv4', protocol: str='tcp',):
        context.network.create_security_group_rule(security_group_id=security_group.id,direction=direction,
            ethertype=ethertype,
            protocol=protocol,
            port_range_min=port_range_min,
            port_range_max=port_range_max,
            remote_ip_prefix=remote_ip_prefix,
        )

    @then("I should be able to delete a security group with name {security_group_name}")
    def delete_a_security_group(context, security_group_name: str):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group, f"Security group with name {security_group_name} does not exist"
        sec_group_list = list()
        for sec_group in context.client.network.security_groups():
            if sec_group.name == security_group_name:
                sec_group_list.append(sec_group.id)
        for sec_group in sec_group_list:
            context.client.network.delete_security_group(name_or_id=sec_group)
        assert not context.client.network.find_security_group(
            name_or_id=security_group_name
        ), f"Security group with name {security_group_name} was not deleted"

    @then("I should be able to create a security group rule for {security_group_name} with direction {direction} "
          "protocol {protocol} and port range {port_range_min} to {port_range_max}")
    def create_security_group_rule(context, security_group_rule_name: str,):
        security_group = context.client.network.find_security_group(name_or_id=security_group_rule_name)
        assert security_group, f"Security group with name {security_group_rule_name} doesn't exist"
        sec_group_rule_list = list()
        for sec_group in context.client.network.security_group_rules():
            if sec_group.name == security_group_rule_name:
                sec_group_rule_list.append(sec_group.id)
        for sec_group in sec_group_rule_list:
            context.client.network.delete_security_group_rule(name_or_id=sec_group.id)

    @then("I should be able to create availability zone named {availability_zone}")
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

    @then("I should be able to create a VM with name {vm_name} using image {image_name} and flavor {flavor_name} on network {network_name}")
    def create_vm(context, vm_name: str, image_name: str, flavor_name: str, network_name: str):
        image = context.client.compute.find_image(name_or_id=image_name)
        assert image, f"Image with name {image_name} doesn't exist"
        flavor = context.client.compute.find_flavor(name_or_id=flavor_name)
        assert flavor, f"Flavor with name {flavor_name} doesn't exist"
        network = context.client.network.find_network(name_or_id=network_name)
        assert network, f"Network with name {network_name} doesn't exist"
        server = context.client.compute.create_server(
            name=vm_name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
        )
        context.client.compute.wait_for_server(server)
        created_server = context.client.compute.find_server(name_or_id=vm_name)
        assert created_server, f"VM with name {vm_name} was not created successfully"

    @then('I should be able to delete the VM with name {vm_name}')
    def delete_vm(context, vm_name: str):
        for vm in context.client.compute.find_server(name_or_id=vm_name):
            context.client.compute.delete_server(context.server.id)
            context.client.compute.wait_for_delete(context.server)
            deleted_server = context.client.compute.find_server(name_or_id=vm.name)
            assert not deleted_server, f"VM with name {vm_name} was not deleted successfully"
    @then("I should be able to create a floating ip on {network_id}")
    def create_floating_ip(context, network_id):
        floating_ip = context.network.create_ip(floating_network_id=network_id)
        for ip in context.network.floating_ips(network_id=network_id):
            if ip == floating_ip.floating_ip_address:





