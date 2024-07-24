@iperf3
@benchmark
Feature: Benchmark Iperf3 VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Given I have deployed hosts in <network_quantity> networks
    And I have a private key at <vm_private_ssh_key_path> for <username>
    Then I should be able to create a checkup script for <conn_test> locally
    Then I should be able to collect all Floating IPs
    Then I should be able to collect all VM IPs and ports
    Then I should be able to SSH into <network_quantity> VMs and perform <conn_test> test
   

    Examples:
	    | host_name    | vm_private_ssh_key_path  | username 	| network_quantity	| conn_test |
			|default-jh  | test-keypair-private	      | ubuntu	  | 1	                | iperf3    |