@ssh
@test
Feature: SSH into VM

	Scenario Outline: Connect to a VM using SSH
		Given I have deployed a VM with IP <vm_ip_address>
		And I have a private key at <keypair_name> for <username>
		Then I should be able to SSH into the VM

		And close the connection

		Examples: Test security groups
			| vm_ip_address    | keypair_name							   | username 	|
			| localhost		     | ./sshKey.pem				         | erik		    |
			| 213.131.230.203	 | ./terraform/private_key.pem | ubuntu		  |
			| 213.131.230.199	 | ./terraform/private_key.pem | ubuntu		  |

