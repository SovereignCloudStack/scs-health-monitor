Feature: OpenStack Network Creation

	Scenario Outline: Connect to OpenStack and create a network
		Given I have the OpenStack environment variables set
		When I connect to OpenStack
		Then I should be able to create a network with name <networkName>

		Examples: Test networks
			| networkName |
			| test02	  |
			| test03	  |