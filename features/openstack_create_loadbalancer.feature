@loadbalancer
@create
Feature: OpenStack Network Creation
	
	Scenario Outline: Connect to OpenStack and create a loadbalancer
		Given I connect to OpenStack
		When A network with name <network_name> exists
		Then I should be able to create <lb_quantity> loadbalancers for <network_name>

		Examples: Test loadbalancers
			| lb_quantity | network_name			|
			| 2	    			| scs-hm-network-1 	|