@ssh
@test
Feature: SSH into VM and test internet connectivity

	Scenario Outline: Connect to a VM using SSH and test internet connectivity
		Given I have deployed a VM with IP <vm_ip_address>
		And I have a private key at <keypair_name> for <username>
		Then I should be able to SSH into the VM
		And be able to communicate with the internet to test <conn_test> connectivity 
		And close the connection

		Examples: Test security groups
			| vm_ip_address    | keypair_name						     		| username 	| conn_test |
			| localhost		     | ./sshKey.pem						        | erik			| ssh				| 
			| 213.131.230.207	 | ./terraform/private_key.pem 		| ubuntu		| ssh				|
			| 213.131.230.199	 | ./terraform/private_key.pem 		| ubuntu		| ssh				|
