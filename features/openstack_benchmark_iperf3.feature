@iperf3
@benchmark
Feature: Benchmark Iperf3 VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Given I have deployed hosts in <network_quantity> networks
    And I have a private key at <vm_private_ssh_key_path> for <username>
    Then I should be able to collect the IP of the host from network
    Then I should be able to SSH into <network_quantity> VMs and perform <conn_test> test
   
   
    ## substeps:
    # Then I should be able to access one of <network_quantity> VMs
    # Then I should be able to create a wait-script and transfer that to the remote machine
    # And run the <conn_test> test between two hosts and parse the test results to log


    Examples:
	    | host_name    | vm_private_ssh_key_path  | username 	| network_quantity	| conn_test |
			|default-jh  | test-keypair-private	      | ubuntu	    | 3	                | iperf3    |