@network
@cleanup
Feature: Delete openstack network

	Scenario Outline: Connect to OpenStack and delete a network
		Given I connect to OpenStack
		When A network with name <network_name> exists
		Then I should be able to delete a network with name <network_name>

		Examples: Test networks
			| network_name |
			| network01	   |
			| network02	   |