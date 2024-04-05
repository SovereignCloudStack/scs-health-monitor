@ssh
@test
Feature: SSH into VM and test internet connectivity

	Scenario Outline: Connect to a VM using SSH and test internet connectivity
		Given I have deployed a VM with IP <vm_ip_address>
		and I have a private key at <vm_private_ssh_key_path>
		Then I should be able to SSH into the VM as user <username>
		And be able to communicate with the internet
		And close the connection

		Examples: Test security groups
			| vm_ip_address      | vm_private_ssh_key_path     		| username 	|
			| localhost		     | ./sshKey.pem						| erik		|
			| 213.131.230.207	 | ./terraform/private_key.pem 		| ubuntu	|