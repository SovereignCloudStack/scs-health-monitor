@vm
@benchmark
@create
@delete
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Given I want to build the benchmark infrastructure by using resources having the infix <test_infix>
    Then I should be able to create a router connected to the external network named <ext_net>
    Then I should be able to fetch availability zones
    Then I should be able to create networks for both the jump hosts and for each availability zone
    Then I should be able to create subnets for both the jump hosts and vms
    Then I should be able to connect the router to the jump host subnet
    Then I should be able to connect the router to the vm subnets
    Then I should be able to create a security group for the hosts allowing inbound tcp connections for the port range <port_start> to <port_end>
    Then I should be able to create <quantity_vms> VMs with a key pair named <keypair_name> and strip them over the VM networks
    Then I should be able to query the ip addresses of the created <quantity_vms> VMs
    Then I should be able to calculate the port forwardings for the jump hosts by associating the VM ip addresses with the jump hosts by az in the port range <port_start> to <port_end>
    Then I should be able to create a jump host for each az using a key pair named <keypair_name>
    Then I should be able to attach floating ips to the jump hosts
   
    Given I have deployed <jh_quantity> JHs
    And I have a private key at <keypair_name> for <username>
    Then I should be able to SSH into <jh_quantity> JHs and test their <conn_test> connectivity

    Examples: Build benchmark infrastructure
    | test_infix | ext_net  | keypair_name          | quantity_vms  | port_start | port_end | username 	|jh_quantity	| conn_test |
    | infra      | ext01    | test-keypair          | 2             |      222   | 229      | ubuntu	  |1	          | ping			|
 