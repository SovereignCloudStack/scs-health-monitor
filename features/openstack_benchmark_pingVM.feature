@vm
@benchmark
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Given I have deployed a VM with IP <vm_ip_address>
    and I have a private key at <vm_private_ssh_key_path>
    Then I should be able to SSH into the VM as user <username>
    Then I should be able to collect all VM IPs
    And be able to ping all IPs to test <conn_test> connectivity
    # Then I should be able to access <jh_quantity> VMs
    # Then all VMs should be able to ping each other to test <conn_test> connectivity
    # TODO: Connectivity through jump hosts isn't implemented.
    #  For this we need redirection rules on those jump hosts VMs which address our VMs.

    Examples:
	    | vm_ip_address    | vm_private_ssh_key_path     			                                            | username 	| jh_quantity	| conn_test |
			| localhost		     | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/features/sshKey	| katha			| 3	          | ping			|

