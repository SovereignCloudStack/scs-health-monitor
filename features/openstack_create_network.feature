@network
@create
Feature: OpenStack Network Creation
	
	Scenario Outline: Connect to OpenStack and create a network
		Given I connect to OpenStack
		Then I should be able to create a network with name <network_name>

		Examples: Test networks
			| network_name |
			| network01	   |
			| network02	   |