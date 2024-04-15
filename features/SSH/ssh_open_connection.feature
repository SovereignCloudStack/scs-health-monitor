@ssh
@test
Feature: SSH into VM

	Scenario Outline: Connect to a VM using SSH
		Given I have deployed a VM with IP <vm_ip_address>
		and I have a private key at <vm_private_ssh_key_path>
		Then I should be able to SSH into the VM as user <username>
		And close the connection

		Examples: Test security groups
			| vm_ip_address    | vm_private_ssh_key_path	   | username 	|
			| localhost		     | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/features/SSH/sshKey	| katha	|
			| 213.131.230.203	 | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/terraform/private_key.pem | ubuntu		  |
			| 213.131.230.199	 | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/terraform/private_key.pem | ubuntu		  |

