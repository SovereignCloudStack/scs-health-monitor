from behave import given, then
import time

import tools

DEFAULT_SECURITY_GROUPS = [{"name": "ssh"}, {"name": "default"}]


class BenchmarkInfra:
    """
    Build test infrastructure on which the benchmarks base on.

    It consists of:

    * a network with jump hosts (one for each availability zone) (jh network),
    * a network for each availability zone (vm network),
    * a router to which all networks are connected and
    * several VMs striped over the available vm networks

    The jump hosts do a port forwarding to the vms.
    TODO: Redirs!
     See usage of PORTS: collectPorts
    """

    @given("I want to build the benchmark infrastructure by using resources having the prefix {prefix}")
    def infra_benchmark(context, prefix: str):
        context.test_name = f"{context.test_name}-{prefix}-"
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

        # List of dicts in order of VM names (asc), az and containing VM ip addresses
        context.az_vm_port_mapping: list = []

        context.collector = tools.Collector(client=context.client)

    @staticmethod
    def derive_vm_name(context, num: int):
        return f"{context.test_name}vm{num}"

    @then("I should be able to create a router connected to the external network named {ext_net}")
    def infra_create_router(context, ext_net):
        nets = tools.list_networks(context.client, filter={"name": ext_net})
        assert len(nets) == 1, "Expecting to find exactly one external network."

        context.collector.create_router(name=context.lb_router_name,
                                        external_gateway_info={'network_id': nets[0].id})

    @then("I should be able to fetch availability zones")
    def infra_get_azs(context):
        azs = tools.get_availability_zones(context.client)
        assert len(azs) > 0, "Expecting presence of availability zones!"
        for az in azs:
            context.azs.append(az["name"])

    @then(
        "I should be able to create networks for both the jump hosts and for each availability zone")
    def infra_create_networks(context):
        context.jh_net_id = context.collector.create_network(f"{context.test_name}jh").id
        for az in context.azs:
            no = context.azs.index(az)
            net = context.collector.create_network(f"{context.test_name}vm-{no}",
                                                   availability_zone_hints=[az])
            context.vm_nets_ids.append(net.id)

    @then("I should be able to create subnets for both the jump hosts and vms")
    def infra_create_subnets(context):
        """
        Create two kinds of subnets: One for the jump host and one for the VMs.
        For the latter we create one subnet for each AZ.
        """
        context.jh_subnet_id = context.collector.create_subnet(name=f"{context.test_name}jh",
                                                               network_id=context.jh_net_id,
                                                               cidr="10.250.255.0/24").id

        for net in context.vm_nets_ids:
            no = context.vm_nets_ids.index(net)
            subnet = context.collector.create_subnet(name=f"{context.test_name}vm-{no}",
                                                     network_id=net,
                                                     cidr=f"10.250.{no * 4}.0/22")
            context.vm_subnet_ids.append(subnet.id)

    @then("I should be able to connect the router to the jump host subnet")
    def infra_connect_router_to_jh_net(context):
        router = tools.find_router(context.client, context.lb_router_name)
        router_update = context.collector.add_interface_to_router(router, context.jh_subnet_id)

        tools.add_value_to_dict_list(context.lb_router_port_ids,
                                     context.lb_router_name,
                                     router_update["port_id"])

    @then("I should be able to connect the router to the vm subnets")
    def infra_connect_router_to_vm_net(context):
        router = tools.find_router(context.client, context.lb_router_name)
        for vm_subnet_id in context.vm_subnet_ids:
            router_update = context.collector.add_interface_to_router(router, vm_subnet_id)

            tools.add_value_to_dict_list(context.lb_router_port_ids,
                                         context.lb_router_name,
                                         router_update["port_id"])

    @then(
        "I should be able to create a jump host for each az using a key pair named {keypair_name}")
    def infra_create_jumphosts(context, keypair_name: str):
        # TODO: Support SNAT and port forwarding
        for az in context.azs:
            no = context.azs.index(az)
            # TODO: Provide AZ, user data containing network config (snat, VIP, masq, packages, internal net),
            #  keypair (pub key only!), jh ports (shouldn't be necessary; network configuration via SSH)
            jh_name = f"{context.test_name}jh{no}"
            context.collector.create_jumphost(jh_name,
                                              context.jh_net_id,
                                              keypair_name,
                                              context.vm_image,
                                              context.flavor_name,
                                              DEFAULT_SECURITY_GROUPS,
                                              availability_zone=az)
            context.lb_jump_host_names.append(jh_name)

    @then("I should be able to attach floating ips to the jump hosts")
    def infra_create_floating_ip(context):
        for jh in context.lb_jump_host_names:
            context.collector.create_floating_ip(jh)

    @then("I should be able to create {quantity:d} VMs with a key pair named {keypair_name} and "
          "strip them over the VM networks")
    def infra_create_vms(context, quantity: int, keypair_name: str):
        for num in range(0, quantity):
            vm_name = BenchmarkInfra.derive_vm_name(context, num)
            assert len(context.vm_nets_ids) > 0, "Number of VM networks has to be greater than 0"
            # Strip VMs over VM networks (basically round-robin)
            vm_net_id = context.vm_nets_ids[num % len(context.vm_nets_ids)]
            context.collector.create_jumphost(vm_name,
                                              vm_net_id,
                                              keypair_name,
                                              context.vm_image,
                                              context.flavor_name,
                                              DEFAULT_SECURITY_GROUPS)

    @then('I should be able to query the ip addresses of the created {quantity:d} VMs')
    def infra_vms_query_ips(context, quantity: int):
        for num in range(0, quantity):
            vm_name = BenchmarkInfra.derive_vm_name(context, num)
            vm = context.collector.find_server(vm_name)
            assert vm, f"Expected that vm with name {vm_name} exists"
            networks = vm["addresses"]
            assert len(networks) == 1, (f"Expecting the VM has exactly one network. "
                                        f"Found {len(networks)}.")
            context.az_vm_port_mapping.append({
                "az": vm["location"]["zone"],
                "vm_name": vm_name,
                "addr": list(networks.values())[0][0]["addr"]
            })

    @then("I should be able to calculate the port forwardings for the jump hosts by associating "
          "the VM ip addresses with the jump hosts by az in the port range {port_start:d} to "
          "{port_end:d}")
    def infra_calculate_port_forwardings(context, port_start: int, port_end: int):
        jhs = []
        for jh_name in context.lb_jump_host_names:
            jh = context.collector.find_server(jh_name)
            jhs.append(jh)

        # Mapping between the jump host ports and the VM ips
        jh_port_mapping = {}

        for mapping in context.az_vm_port_mapping:
            for jh in jhs:
                jh_name = jh["name"]
                # found a jump host in the same az as the vm
                if mapping["az"] == jh["location"]["zone"]:
                    tools.add_value_to_dict_list(jh_port_mapping, jh_name, [])
                    # Get next free port
                    port = port_start + len(jh_port_mapping[jh_name])
                    assert port <= port_end, "We exceed the supplied port range"
                    jh_port_mapping[jh_name].append([port, mapping["addr"], mapping["vm_name"]])

        # TODO: Test this!
        print("!!!", jh_port_mapping)


    @then("I sleep")
    def sleep(context):
        # TODO: Just for testing
        time.sleep(600)

    @then("I should be able to delete all subnets of routers")
    def infra_router_delete_subnets(context):
        for router_subnet in context.collector.router_subnets:
            context.collector.delete_interface_from_router(router_subnet["router"],
                                                           router_subnet["subnet"])

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
