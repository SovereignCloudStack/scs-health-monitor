@ssh
@test
Feature: SSH into VM and test network connectivity

	Scenario Outline: Connect to a VM using SSH and test network connectivity
		Given I have deployed a VM with IP <vm_ip_address>
		And I have a private key at <keypair_name>
		Then I should be able to SSH into the VM as user <username>
		And be able to communicate with <ip> to test <conn_test> connectivity 
		And close the connection

		Examples: Test security groups
			| vm_ip_address      | keypair_name     		| username 			| ip			| conn_test |
			| localhost		     | ./test_ssh												| piotrbigos		| 1.2.3.4	| ssh				|
			| localhost		     | ./test_ssh												| piotrbigos		| 8.8.8.8	| ssh				|
			| 213.131.230.207	 | ./terraform/private_key.pem 			| ubuntu				| 8.8.8.8	| ssh				| 
			| 213.131.230.199	 | ./terraform/private_key.pem 			| ubuntu				| 8.8.8.8	| ssh				| 