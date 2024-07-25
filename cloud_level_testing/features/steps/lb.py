from behave import given, then

from definitions import StepsDef
import libs.static
import tools


class LbStepsDef:
    @given("I want to test loadbalancers by using resources having the postfix {postfix}")
    def lbs_benchmark(context, postfix: str):
        postfix = f"-{postfix}-"
        context.test_name = f"{libs.static.get_tests_name_identification(context, postfix)}"
        context.vm_nets_ids: list = []
        context.jh_net_id = None

    @then("I should be able to create a router connected to the external network named {ext_net}")
    def lb_create_routers(context, ext_net):
        router = tools.create_router(context.client,
                                     name=f"{context.test_name}router")
        nets = tools.list_networks(context.client, filter={"name": ext_net})
        assert len(nets) == 1, "Expecting to find exactly one external network."
        #ext_gateway_net_id=nets[0].id
        # TODO: Add external gateway! To do so we need to find out which parameters (in body) OpenStack needs from us..
        #tools.router_add_external_gateways(context.client, router, body={})

    @then(
        "I should be able to create a network for both the jump hosts and for each availability "
        "zone")
    def lb_create_networks(context):
        context.jh_net_id = (
            tools.create_network(context.client, f"{context.test_name}jh").id)
        azs = tools.get_availability_zones(context.client)
        assert len(azs) > 0, "Expecting presence of availability zones!"
        for az in azs:
            net = tools.create_network(context.client,
                                       f"{context.test_name}{az.name}",
                                       availability_zone_hints=[az.name])
            context.vm_nets_ids.append(net.id)

    @then("I should be able to create subnets for both the jump hosts and vms")
    def lb_create_subnets(context):
        """
        Create two kinds of subnets: One for the jump hosts and one for the VMs.
        For the latter we create one subnet for each AZ.
        """
        tools.create_subnet(context.client,
                            name=f"{context.test_name}jh",
                            network_id=context.jh_net_id,
                            cidr="10.250.255.0/24")
        for net in context.vm_nets_ids:
            no = context.vm_nets_ids.index(net) + 1
            tools.create_subnet(context.client,
                                name=f"{context.test_name}vm{no}",
                                network_id=net,
                                cidr=f"10.250.{no * 4}.0/24")

    @then("I should be able to create a jump host for each az")
    def lb_create_jumphosts(context):
        # TODO: Support SNAT and port forwarding
        for net in context.vm_nets_ids:
            no = context.vm_nets_ids.index(net) + 1
            # TODO: Provide AZ, user data containing network config (snat, VIP, masq, packages, internal net),
            #  keypair (pub key only!), jh ports (shouldn't be necessary; network configuration via SSH)
            tools.create_jumphost(context.client,
                                  f"{context.test_name}jh{no}",
                                  None,
                                  None,
                                  context.vm_image,
                                  context.flavor_name)

    @then("I should be able to create {quantity:d} VMs for the LBs")
    def lb_create_vms(context, quantity):
        for num in range(0, quantity):
            vm_name = f"{context.test_name}{num}"
            # TODO: Create networks!
            network = None
            tools.create_vm(context.client, vm_name, context.vm_image, context.flavor_name,
                            network)

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
