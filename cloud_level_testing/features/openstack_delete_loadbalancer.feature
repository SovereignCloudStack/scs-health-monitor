@loadbalancer
@cleanup
Feature: Delete openstack loadbalancer

	Scenario: Connect to OpenStack and delete a loadbalancer
		Given I connect to OpenStack
		Then I should be able to delete a loadbalancer
