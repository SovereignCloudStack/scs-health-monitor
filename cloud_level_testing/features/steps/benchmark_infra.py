from behave import given, then
import time
import jinja2
import base64

import tools

DEFAULT_SECURITY_GROUPS = ["ssh", "default", "ping-sg"]
DEFAULT_IPERF3_PORT = 5201


class BenchmarkInfra:
    """
    Build test infrastructure on which the benchmarks base on.

    It consists of:

    * a network with jump hosts (one for each availability zone) (jh network),
    * a network for each availability zone (vm network),
    * a router to which all networks are connected and
    * several VMs striped over the available vm networks

    The jump hosts do a port forwarding to the vms. The first VM can be reached via port 222
    on the jump host, the second VM via port 223 and so on.
    """

    @given(
        "I want to build the benchmark infrastructure by using resources having the infix "
        "{infix}")
    def infra_benchmark(context, infix: str):
        context.test_name = f"{context.test_name}-{infix}-"
        context.vm_nets_ids: list = []
        context.azs: list = []
        context.vm_subnet_ids: list = []
        context.jh_net_id = None
        context.jh_subnet_id = None
        context.lb_router_name = f"{context.test_name}router"
        # Dict of router names with their corresponding port ids
        # { "router_name": ["id1", "id2"] }
        context.lb_router_port_ids: dict = {}

        # List of dicts in order of VM names (asc), az and containing VM ip addresses
        context.az_vm_port_mapping: list = []

        # Security group name the jump hosts will use for port forwardings
        context.host_sec_group_name = f"{context.test_name}jumphost"

        context.collector.client = context.client

    @staticmethod
    def derive_vm_name(context, num: int):
        return f"{context.test_name}vm{num}"

    @staticmethod
    def calculate_jh_name_by_az(context, az):
        return f"{context.test_name}jh{context.azs.index(az)}"

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

    @then("I should be able to create networks for both the jump hosts and for each availability "
          "zone")
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

    @then("I should be able to create a security group for the hosts allowing inbound tcp "
          "connections for the port range {port_start:d} to {port_end:d}")
    def create_security_group(context, port_start: int, port_end: int):
        sg = context.collector.create_security_group(
            context.host_sec_group_name,
            "Allow ssh redirection inside network and iperf3"
        )
        context.collector.create_security_group_rule(sg["id"], "tcp", port_start, port_end)
        context.collector.create_security_group_rule(
            sg["id"],
            "tcp",
            DEFAULT_IPERF3_PORT,
            DEFAULT_IPERF3_PORT,
            remote_ip_prefix="10.0.0.0/8",
        )
        context.collector.create_security_group_rule(sg["id"], "icmp", remote_ip_prefix="0.0.0.0/0")
        #TODO only inner network maybe rewrite pingVM feature to ping only inner network remote_ip_prefix="10.0.0.0/8"

    @then(
        "I should be able to create a jump host for each az using a key pair named {keypair_name}")
    def infra_create_jumphosts(context, keypair_name: str):
        for az in context.azs:
            jh_name = BenchmarkInfra.calculate_jh_name_by_az(context, az)

            forwarding_script_tmpl = r"""#!/bin/bash
set -e

# Set masquerading + port forwardings to vms

# determine default interface
echo -n $(ip route show | grep ^default | head -n1 | sed 's@default via [^ ]* dev \([^ ]*\) .*@\1@g') > /tmp/iface
# Outbound Masquerading
iptables -t nat -A POSTROUTING -o $(cat /tmp/iface) -s 10.250/16 -j MASQUERADE
iptables -P FORWARD DROP
iptables -I FORWARD 1 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
iptables -I FORWARD 2 -i $(cat /tmp/iface) -o $(cat /tmp/iface) -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -I FORWARD 3 -i $(cat /tmp/iface) -o $(cat /tmp/iface) -s 10.250/16 -j ACCEPT
# Set ip_forward
echo 1 > /proc/sys/net/ipv4/ip_forward
# Inbound Masquerading
iptables -I FORWARD 4 -i $(cat /tmp/iface) -o $(cat /tmp/iface) -d 10.250/16 -p tcp --dport 22 -j ACCEPT
iptables -t nat -A POSTROUTING -o $(cat /tmp/iface) -d 10.250/16 -p tcp --dport 22 -j MASQUERADE
# Forwardings to vms
{%- for redir in redirs[jh_name]["vms"] %}
iptables -t nat -A PREROUTING -s 0/0 -i $(cat /tmp/iface) -j DNAT -p tcp --dport {{ redir["port"] }} --to-destination {{ redir["addr"] ~ ":22" }}
{% endfor %}
"""

            template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
                forwarding_script_tmpl)
            forwarding_script = template.render(redirs=context.redirs, jh_name=jh_name)

            user_data = f"""#cloud-config
packages:
- iperf3
- jq

# A little bit hacky: We provide the script base64 encoded,
# otherwise cloud-init complains about invalid characters.
# We then execute the actual script after base64-decoding it.

write_files:
- content: {(base64.b64encode(str(forwarding_script).encode('ascii'))).decode('ascii')}
  path: /tmp/set-ip-forwardings-base64
  permissions: '0755'
- content: ''
  path: /tmp/set-ip-forwardings.sh
  permissions: '0755'
        
runcmd:
- cat /tmp/set-ip-forwardings-base64 | base64 -d > /tmp/set-ip-forwardings.sh
- /tmp/set-ip-forwardings.sh
# run iperf3 as deamon from server
- iperf3 -Ds 
"""

            context.collector.create_jumphost(jh_name,
                                              context.jh_net_id,
                                              keypair_name,
                                              context.vm_image,
                                              context.flavor_name,
                                              DEFAULT_SECURITY_GROUPS + [
                                                  context.host_sec_group_name
                                              ],
                                              availability_zone=az,
                                              userdata=user_data,
                                              )

    @then("I should be able to attach floating ips to the jump hosts")
    def infra_create_floating_ip(context):
        for az in context.azs:
            # fip = context.collector.create_floating_ip(
            #     BenchmarkInfra.calculate_jh_name_by_az(context, az)
            # )
            fip = tools.attach_floating_ip_to_server(context, BenchmarkInfra.calculate_jh_name_by_az(context, az))
            # Add jump host internal ip and fip to port forwardings data structure
            for jh_name, redir in context.redirs.items():
                if jh_name == BenchmarkInfra.calculate_jh_name_by_az(context, az):
                    context.redirs[jh_name]["fip"] = str(fip)
                # Also set fixed ip of network
                if not context.redirs[jh_name]["addr"]:
                    jh = context.collector.find_server(jh_name)
                    context.redirs[jh_name]["addr"] = (
                        tools.vm_extract_ip_by_type(jh, "fixed"))

    @then("I should be able to create {quantity:d} VMs with a key pair named {keypair_name} and "
          "strip them over the VM networks")
    def infra_create_vms(context, quantity: int, keypair_name: str):
        user_data = f'''#cloud-config
packages:
- iperf3
- jq
        '''
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
                                              DEFAULT_SECURITY_GROUPS + [
                                                  context.host_sec_group_name
                                              ],
                                              userdata=user_data,)

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
        """
        Calculate port forwarding for jump hosts redirecting ssh to the actual vms.
        The resulting dict contains for each jump host (we didn't create them, yet)
        a list of related vms (= vms located in the same az as the jump host) including
        their internal ips and an associated port inside the range [port_start, port_end]
        which the jump host will use for redirecting traffic to the vm.

        The resulting dict looks like:
        {
          'scs-hm-infra-jh0': {
            'addr': None,
            'fip': None,
            'vms': [
              {
                'port': 222,
                'addr': '10.250.3.73',
                'vm_name': 'scs-hm-infra-vm0'
              },
              {
                'port': 223,
                'addr': '10.250.0.8',
                'vm_name': 'scs-hm-infra-vm1'
              }
            ]
          }
        }

        @param port_start: first port to allocate for redirection
        @param port_end: lost port the allocate for redirection
        @return:
        """
        # Mapping between the jump host ports and the VM ips
        redirs = {}

        for mapping in context.az_vm_port_mapping:
            for az in context.azs:
                jh_name = BenchmarkInfra.calculate_jh_name_by_az(context, az)
                # Assuming a jump host (we wil create them later) in the same az as the vm
                if mapping["az"] == az:
                    if jh_name not in redirs:
                        redirs[jh_name] = {
                            "fip": None,  # Add after jump host created
                            "addr": None,
                            "vms": []
                        }
                    # Get next free port
                    port = port_start + len(redirs[jh_name]["vms"])
                    assert port <= port_end, "We exceed the supplied port range"
                    redirs[jh_name]["vms"].append({
                        "port": port,
                        "addr": mapping["addr"],
                        "vm_name": mapping["vm_name"]
                    })

        context.redirs = redirs

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

    @then('I can pass the context to another feature')
    def step_then_use_in_another_feature(context):
        context.shared_context.test_name = context.test_name
        context.shared_context.redirs = context.redirs
        context.shared_context.keypair_name = context.keypair_name
        assert hasattr(context.shared_context,'redirs'), f"context could not be passed"
