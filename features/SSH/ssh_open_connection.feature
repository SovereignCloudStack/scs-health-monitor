@ssh
@test
Feature: SSH into VM in openstack

	Scenario Outline: Connect to a VM using SSH
		Given I have deployed a VM with IP <vm_ip_address>
		and I have a private key at <vm_private_ssh_key_path>
		Then I should be able to SSH into the VM as user <username>
		And close the connection

		Examples: Test security groups
			| vm_ip_address      | vm_private_ssh_key_path	| username 	|
			| localhost		     | ./sshKey.pem				| erik		|