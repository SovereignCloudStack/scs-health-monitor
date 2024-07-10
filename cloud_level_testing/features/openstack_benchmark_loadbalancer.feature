@loadbalancer
@benchmark
Feature: Test load balancer

  Scenario Outline: Create load balancers and check whether VMs can be reached through their endpoint
    Given I connect to OpenStack
    Then I should be able to create <lb_quantity> loadbalancers for <subnet_name> in network <network_name>
    Then I should be able to create loadbalancer listeners
    Then I should be able to create loadbalancer pools
    Then I should be able to create loadbalancer members
    #Then I should be able to access VMs through loadbalancers

    # Kill some backends
    #When I kill the backend of load balancer members
    #Then the load balancer pool should have degraded members
    #Then I should be able to access VMs through loadbalancers

    Examples: Test loadbalancer
    | lb_quantity | subnet_name		| network_name 	|
    | 1	   		  | scs-hm-subnet-1 | no-relevance  |
