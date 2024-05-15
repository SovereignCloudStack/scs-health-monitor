@loadbalancer
@create
Feature: OpenStack Network Creation
	
	Scenario Outline: Connect to OpenStack and create a loadbalancer
		Given I connect to OpenStack
		When A subnet with name <subnet_name> exists in network <network_name>
		Then I should be able to create <lb_quantity> loadbalancers for <subnet_name> in network <network_name>

		Examples: Test loadbalancers
			| lb_quantity | subnet_name			| network_name 			|
			| 1	    			| scs-hm-subnet-1 | scs-hm-network-1	|