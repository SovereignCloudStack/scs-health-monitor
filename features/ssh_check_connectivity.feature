@ssh
@test
Feature: SSH into VM and test network connectivity

	Scenario Outline: Connect to a VM using SSH and test network connectivity
		Given I have deployed a VM with IP <vm_ip_address>
		And I have a private key at <vm_private_ssh_key_path>
		Then I should be able to SSH into the VM as user <username>
		And be able to communicate with <ip>
		And close the connection

		Examples: Test security groups
			| vm_ip_address      | vm_private_ssh_key_path     		| username 			| ip	|
			| localhost		     | ./test_ssh												| piotrbigos		| 1.2.3.4	|
			| localhost		     | ./test_ssh												| piotrbigos		| 8.8.8.8	|
			| 213.131.230.207	 | ./terraform/private_key.pem 			| ubuntu				| 8.8.8.8	|
			| 213.131.230.199	 | ./terraform/private_key.pem 			| ubuntu				| 8.8.8.8	|
