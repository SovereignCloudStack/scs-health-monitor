@vm
@benchmark
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Then I sjhould be able to collect all 
    and I have a private key at <vm_private_ssh_key_path>
    Then I should be able to access <vms_quantity> VMs
    Then all VMs should be able to ping each other
    # TODO: Connectivity through jump hosts isn't implemented.
    #  For this we need redirection rules on those jump hosts VMs which address our VMs.

    Examples:
	    | vm_ip_address    | vm_private_ssh_key_path     			| username 	| jh_quantity	|
			| localhost		     | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/features/SSH/sshKey	| katha			    | 3	|
			| localhost		     | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/features/SSH/sshKey	| katha			    | 3	|
#			| 213.131.230.157	 | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/terraform/private_key.pem | ubuntu		| 3	|