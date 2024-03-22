from environment_setup import before_all, after_all
import yaml
from behave import given, when, then
import openstack


def before_all(context):
    before_all(context)

def after_all(context):
    after_all(context)


class StepsDef:

    @given('I connect to OpenStack')
    def given_i_connect_to_openstack(context):
        context.client = openstack.connect(cloud="gx")

    @when('A router with name {router_name} exists')
    def when_a_router_with_name_exists(context, router_name: str):
        router = context.client.network.find_router(name_or_id=router_name)
        assert router is not None, f"Router with {router_name} doesn't exist"

    @when('A network with name {network_name} exists')
    def when_i_connect_to_openstack(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"

    @when('A subnet with name {subnet_name} exists in network {network_name}')
    def when_a_subnet_with_name_exists_in_network(context, subnet_name: str, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with name {network_name} does not exist"
        subnet = context.client.network.find_subnet(name_or_id=subnet_name)
        assert subnet is not None, f"Subnet with name {subnet_name} does not exist in network {network_name}"

    @when('A security group with name {security_group_name} exists')
    def when_a_security_group_with_name_exists(context, security_group_name: str):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group is not None, f"Security group with name {security_group_name} doesn't exist"

    @when(
        'A security group rule for {security_group_name} with direction {direction}'
        ' protocol {protocol} and port range {port_range_min} to {port_range_max} exists')
    def step_impl(context, security_group_name, direction, protocol, port_range_min, port_range_max):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group, f"Security group with name {security_group_name} does not exist"
        security_group_rules = list(context.client.network.security_group_rules(
            security_group_id=security_group.id,
            direction=direction,
            ethertype='IPv4',
            protocol=protocol,
            port_range_min=port_range_min,
            port_range_max=port_range_max,
            remote_ip_prefix='0.0.0.0/0'
        ))
        assert len(security_group_rules) > 0, (f"No matching security group rule found for {security_group_name}"
                                               f" with direction {direction}, protocol {protocol},"
                                               f" and port range {port_range_min} to {port_range_max}")

    @then('I should be able to list routers')
    def then_i_should_be_able_to_list_routers(context):
        routers = context.client.network.routers()
        assert routers, "Failed to list routers. No routers found."

    @then('I should be able to create a router with name {router_name}')
    def then_i_should_be_able_to_create_a_router(context, router_name: str):
        router = context.client.network.create_router(name=router_name)
        assert router is not None, f"Failed to create router with name {router_name}"

    @then('I should be able to delete a router with name {router_name}')
    def then_i_should_be_able_to_delete_a_router(context, router_name: str):
        router = context.client.network.find_router(name_or_id=router_name)
        assert router is not None, f"Router with name {router_name} doesn't exist"
        context.client.network.delete_router(router)
        assert not context.client.network.find_router(
            name_or_id=router_name), f"Router with name {router_name} was not deleted"

    @then('I should be able to list networks')
    def then_i_should_be_able_to_list_networks(context):
        networks = context.client.network.networks()
        assert networks, "Failed to list networks. No networks found."

    @then('I should be able to create a network with name {network_name}')
    def then_i_should_be_able_to_create_a_network(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is None, f"Network with {network_name} already exists"
        network = context.client.network.create_network(name=network_name)
        assert not context.client.network.find_network(
            name_or_id=network), f"Network called {network} created"


    @then('I should be able to delete a network with name {network_name}')
    def then_i_should_be_able_to_delete_a_network(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"
        context.client.network.delete_network(network)
        assert not context.client.network.find_network(name_or_id=network), \
            f"Network called {network_name} already deleted"

    @then('I should be able to create a jumphost with name {jumphost_name}')
    def then_i_should_be_able_to_create_a_jumphost(context, jumphost_name: str):
        server = context.client.network.find_network(name_or_id=jumphost_name)
        assert server is None, f"Jumphost with {jumphost_name} already exists"
        context.client.compute.create_server(name=jumphost_name)
        context.client.network.delete_network(server)
        assert context.client.network.find_network(
            name_or_id=server), f"Jumphost called {jumphost_name} created"
        assert not context.client.network.find_network(name_or_id=network),\
            f"Network called {network_name} already deleted"

    @then('I should be able to list subnets')
    def then_i_should_be_able_to_list_subnets(context):
        subnets = context.client.network.subnets()
        assert subnets, "Failed to list subnets. No subnets found."

    @then('I should be able to create a subnet with name {subnet_name} in network {network_name} with {cidr}')
    def then_i_should_be_able_to_create_a_subnet(context, subnet_name: str, network_name: str, cidr):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with name {network_name} does not exist"
        subnet = context.client.network.create_subnet(name=subnet_name, network_id=network.id, ip_version=4,
                                                      cidr=cidr)
        assert not context.client.network.find_network(name_or_id=subnet), f"Failed to create subnet with name {subnet}"

    @then('I should be able to delete a subnet with name {subnet_name}')
    def then_i_should_be_able_to_delete_a_subnet(context, subnet_name: str):
        subnet = context.client.network.find_subnet(name_or_id=subnet_name)
        assert subnet is not None, f"Subnet with name {subnet_name} does not exist"
        context.client.network.delete_subnet(subnet.id)
        assert not context.client.network.find_subnet(
            name_or_id=subnet_name), f"Subnet with name {subnet_name} was not deleted"

    @then('I should be able to create a security group with name {security_group_name} with {description}')
    def then_i_should_be_able_to_create_a_security_group(context, security_group_name: str, description: str):
        security_groups = context.client.network.security_groups()
        assert security_group_name not in security_groups, f"security group named: {security_group_name} already exists"
        security_group = context.client.network.create_security_group(
            name=security_group_name,
            description=description)
        assert security_group is not None, f"Security group with name {security_group.name} was not found"

    @then('I should be able to delete a security group with name {security_group_name}')
    def then_i_should_be_able_to_delete_a_security_group(context, security_group_name: str):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group, f"Security group with name {security_group_name} does not exist"

        context.client.network.delete_security_group(security_group)
        assert not context.client.network.find_security_group(
            name_or_id=security_group_name), f"Security group with name {security_group_name} was not deleted"

    @then(
        'I should be able to create a security group rule for {security_group_name} with'
        ' direction {direction} protocol {protocol} and port range {port_range_min} to {port_range_max}')
    def then_i_should_be_able_to_create_security_rule(context, security_group_name: str,
                                                      direction: str, protocol: str,
                                                      port_range_min: int, port_range_max: int):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group, f"Security group with name {security_group_name} doesn't exist"

        security_group_rule = context.client.network.create_security_group_rule(
            security_group_id=security_group.id,
            direction=direction,
            ethertype='IPv4',
            protocol=protocol,
            port_range_min=port_range_min,
            port_range_max=port_range_max,
            remote_ip_prefix='0.0.0.0/0')

        assert security_group_rule, "Failed to create security group rule"

    @then(
        'I should be able to delete the security group rule for {security_group_name} with direction {direction}'
        ' protocol {protocol} and port range {port_range_min} to {port_range_max}')
    def then_i_should_be_able_to_delete_security_rule(context, security_group_name: str, direction: str, protocol: str,
                                                      port_range_min: int, port_range_max: int):
        security_group = context.client.network.find_security_group(name_or_id=security_group_name)
        assert security_group, f"Security group with name {security_group_name} does not exist"

        rules = list(context.client.network.security_group_rules(
            security_group_id=security_group.id,
            direction=direction,
            ethertype='IPv4',
            protocol=protocol,
            port_range_min=port_range_min,
            port_range_max=port_range_max,
            remote_ip_prefix='0.0.0.0/0'
        ))
        assert len(rules) > 0, (f"No matching security group rule found for {security_group_name}"
                                               f" with direction {direction}, protocol {protocol},"
                                               f" and port range {port_range_min} to {port_range_max}")
        rule_to_delete = rules[0]
        assert rule_to_delete, "Security group rule does not exist"

        context.client.network.delete_security_group_rule(rule_to_delete.id)

        assert not context.client.network.find_security_group_rule(
            name_or_id=rule_to_delete.id), f"Security group rule for {security_group_name} was not deleted"
