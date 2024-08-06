@network
@create
Feature: OpenStack Network Creation
	
	Scenario Outline: Connect to OpenStack and create a network
		Given I connect to OpenStack
		Then I should be able to create <network_quantity> networks

		Examples: Test networks
			| network_quantity |
			| 2	    					 |