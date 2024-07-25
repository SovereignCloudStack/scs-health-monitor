from behave import given, then

from definitions import StepsDef
import libs.static
import tools

DEFAULT_SECURITY_GROUPS = [{"name": "ssh"}, {"name": "default"}]


class LbStepsDef:
    @given("I want to test loadbalancers by using resources having the postfix {postfix}")
    def lbs_benchmark(context, postfix: str):
        postfix = f"-{postfix}-"
        context.test_name = f"tf{postfix}"
        context.vm_nets_ids: list = []
        context.azs: list = []
        context.vm_subnet_ids: list = []
        context.jh_net_id = None
        context.jh_subnet_id = None
        context.lb_router_name = f"{context.test_name}router"
        # Dict of router names with their corresponding port ids
        # { "router_name": ["id1", "id2"] }
        context.lb_router_port_ids: dict = {}
        context.lb_jump_host_names: list = []

    @then("I should be able to create a router connected to the external network named {ext_net}")
    def lb_create_router(context, ext_net):
        nets = tools.list_networks(context.client, filter={"name": ext_net})
        assert len(nets) == 1, "Expecting to find exactly one external network."

        tools.create_router(context.client,
                            name=context.lb_router_name,
                            external_gateway_info={'network_id': nets[0].id})

    @then("I should be able to fetch availability zones")
    def lb_get_azs(context):
        azs = tools.get_availability_zones(context.client)
        assert len(azs) > 0, "Expecting presence of availability zones!"
        for az in azs:
            context.azs.append(az["name"])

    @then("I should be able to create networks for both the jump hosts and for each availability zone")
    def lb_create_networks(context):
        context.jh_net_id = (
            tools.create_network(context.client, f"{context.test_name}jh").id)
        for az in context.azs:
            net = tools.create_network(context.client,
                                       f"{context.test_name}{az}",
                                       availability_zone_hints=[az])
            context.vm_nets_ids.append(net.id)

    @then("I should be able to create subnets for both the jump hosts and vms")
    def lb_create_subnets(context):
        """
        Create two kinds of subnets: One for the jump host and one for the VMs.
        For the latter we create one subnet for each AZ.
        """
        context.jh_subnet_id = tools.create_subnet(context.client,
                                                   name=f"{context.test_name}jh",
                                                   network_id=context.jh_net_id,
                                                   cidr="10.250.255.0/24").id
        for net in context.vm_nets_ids:
            no = context.vm_nets_ids.index(net)
            subnet = tools.create_subnet(context.client,
                                         name=f"{context.test_name}vm{no}",
                                         network_id=net,
                                         cidr=f"10.250.{(no + 1) * 4}.0/24")
            context.vm_subnet_ids.append(subnet.id)

    @then("I should be able to connect the router to the jump host subnet")
    def lb_connect_router_to_jh_net(context):
        router = tools.find_router(context.client, context.lb_router_name)
        iface = tools.add_interface_to_router(context.client, router, context.jh_subnet_id)

        tools.add_value_to_dict_list(context.lb_router_port_ids,
                                     context.lb_router_name,
                                     iface["port_id"])

    @then("I should be able to connect the router to the vm subnets")
    def lb_connect_router_to_vm_net(context):
        router = tools.find_router(context.client, context.lb_router_name)
        for vm_subnet_id in context.vm_subnet_ids:
            iface = tools.add_interface_to_router(context.client, router, vm_subnet_id)

            tools.add_value_to_dict_list(context.lb_router_port_ids,
                                         context.lb_router_name,
                                         iface["port_id"])

    @then("I should be able to create a jump host for each az using a key pair named {keypair_name}")
    def lb_create_jumphosts(context, keypair_name: str):
        # TODO: Support SNAT and port forwarding
        for az in context.azs:
            no = context.azs.index(az)
            # TODO: Provide AZ, user data containing network config (snat, VIP, masq, packages, internal net),
            #  keypair (pub key only!), jh ports (shouldn't be necessary; network configuration via SSH)
            jh_name = f"{context.test_name}jh{no}"
            tools.create_jumphost(context.client,
                                  jh_name,
                                  context.jh_net_id,
                                  keypair_name,
                                  context.vm_image,
                                  context.flavor_name,
                                  DEFAULT_SECURITY_GROUPS,
                                  availability_zone=az)
            context.lb_jump_host_names.append(jh_name)

    @then("I should be able to attach floating ips to the jump hosts")
    def lb_create_floating_ip(context):
        for jh in context.lb_jump_host_names:
            tools.create_floating_ip(context.client, jh)

    @then("I should be able to create {quantity:d} VMs with a key pair named {keypair_name} and strip them over the VM networks")
    def lb_create_vms(context, quantity, keypair_name: str):
        for num in range(0, quantity):
            vm_name = f"{context.test_name}vm{num}"
            assert len(context.vm_nets_ids) > 0, "Number of VM networks has to be greater than 0"
            vm_net_id = context.vm_nets_ids[num % len(context.vm_nets_ids)]
            tools.create_jumphost(context.client,
                                  vm_name,
                                  vm_net_id,
                                  keypair_name,
                                  context.vm_image,
                                  context.flavor_name,
                                  DEFAULT_SECURITY_GROUPS)

    @then("I should be able to create a loadbalancer")
    # TODO: Remove composit, and move to individual functions
    #  We test all functionality in this method first, before moving it to different ones
    #  Here we create all required LB components.
    #  TODO: Finish this by spawning Jump Host and VMs. We want to access web services on the VMs via the JH.
    def lb_create_combat(context):
        lb_name = context.test_name
        tools.create_lb(context.client, name=lb_name,
                        vip_subnet_id="02390af9-7213-46d5-82b8-36af3734406e")
        lb_id = "f9963732-1858-4215-9553-8831d162f852"
        context.client.load_balancer.create_listener(name="listener", protocol="HTTP",
                                                     protocol_port=80, load_balancer_id=lb_id)
        pool_name = "pool"
        context.client.load_balancer.create_pool(name=pool_name,
                                                 protocol="HTTP",
                                                 lb_algorithm="ROUND_ROBIN",
                                                 loadbalancer_id=lb_id)
        pool_id = "8d01205d-d367-4018-ab35-124494ed6258"
        # TODO: Access VM address
        context.client.load_balancer.create_member(pool_id, name="member-1",
                                                   subnet="scs-hm-subnet-1",
                                                   address="10.30.40.139", protocol_port=80)
