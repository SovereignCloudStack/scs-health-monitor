Feature: Delete openstack network

	Scenario Outline: Connect to OpenStack and delete a network
		Given I have the OpenStack environment variables set
		When I connect to OpenStack
		And A network with name <network_name> exists
		Then I should be able to delete a network with name <network_name>

		Examples: Test networks
			| network_name |
			| test02	   |
			| test03	   |