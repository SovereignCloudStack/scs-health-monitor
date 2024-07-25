@loadbalancer
@benchmark
Feature: Test loadbalancer

  Scenario Outline: Create load balancers and check whether VMs can be reached through their endpoint
    Given I connect to OpenStack
    Given I want to build the benchmark infrastructure by using resources having the prefix <test_prefix>
    Then I should be able to create a router connected to the external network named <ext_net>
    # TODO: create secondary VM network (create2ndSubNets) and add network name to VMs
    Then I should be able to fetch availability zones
    Then I should be able to create networks for both the jump hosts and for each availability zone
    Then I should be able to create subnets for both the jump hosts and vms
    Then I should be able to connect the router to the jump host subnet
    Then I should be able to connect the router to the vm subnets
    # TODO: Create security group "scs-hm-infra-jumphost" with forwarding of tcp 222 to 229 for JH VM
    Then I should be able to create a jump host for each az using a key pair named <keypair_name>
    Then I should be able to attach floating ips to the jump hosts
    Then I should be able to create <quantity_vms> VMs with a key pair named <keypair_name> and strip them over the VM networks
    Then I should be able to query the ip addresses of the created <quantity_vms> VMs
    Then I should be able to calculate the port forwardings for the jump hosts by associating the VM ip addresses with the jump hosts by az in the port range <port_start> to <port_end>

    # TODO: Just for testing
    Then I sleep

    Then I should be able to delete the VMs
    Then I should be able to delete all subnets of routers
    Then I should be able to delete routers
    Then I should be able to delete a networks

    #Then I should be able to delete the ports associated with the router

#    Then I should be able to create a loadbalancer
    #Then I should be able to create loadbalancer listeners
    #Then I should be able to create loadbalancer pools
    #Then I should be able to create loadbalancer members
    #Then I should be able to access VMs through loadbalancers

    # Kill some backends
    #When I kill the backend of load balancer members
    #Then the load balancer pool should have degraded members
    #Then I should be able to access VMs through loadbalancers

    Examples: Test loadbalancer
    | test_prefix | ext_net | keypair_name | quantity_vms | port_start | port_end
    | infra           |    ext01    |    tf-id-rsa      | 2 |      222    | 229

    # openstack loadbalancer create --name lb1 --vip-subnet-id public-subnet --wait
    # openstack loadbalancer listener create --name listener1 --protocol HTTP --protocol-port 80 --wait lb1
    # openstack loadbalancer pool create --name pool1 --lb-algorithm ROUND_ROBIN --listener listener1 --protocol HTTP --wait
    # openstack loadbalancer member create --subnet-id private-subnet --address 192.0.2.10 --protocol-port 80 --wait pool1
    # openstack loadbalancer member create --subnet-id private-subnet --address 192.0.2.11 --protocol-port 80 --wait pool1
