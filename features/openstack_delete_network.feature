Feature: Delete openstack network

	Scenario Outline: Connect to OpenStack and delete a network
		Given I have the OpenStack environment variables set
		When I connect to OpenStack
		And A network with name <networkName> exists
		Then I should be able to delete a network with name <networkName>

		Examples: Test networks
			| networkName |
			| test02	  |
			| test03	  |