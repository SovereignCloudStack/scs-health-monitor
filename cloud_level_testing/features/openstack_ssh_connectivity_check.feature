@ssh
@test
Feature: SSH into VM and test network connectivity

	Scenario Outline: Connect to a VM using SSH and test network connectivity
		Given I have deployed a VM with IP <vm_ip_address>
		And I have a private key at <keypair_name> for <username>
		Then I should be able to SSH into the VM
		And be able to communicate with <ip> to test <conn_test> connectivity 
		And close the connection

		Examples: Test security groups
			| vm_ip_address     | keypair_name     	| username 	| ip			| conn_test |
			| 213.131.230.11 		| test-keypair	 		| ubuntu		| 8.8.8.8	| ssh				|
	#		| 213.131.230.11 		| test-keypair	 		| ubuntu		| 1.2.3.4 | ssh				|