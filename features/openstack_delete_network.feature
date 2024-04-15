@network
@cleanup
Feature: Delete openstack network

	Scenario: Connect to OpenStack and delete a network
		Given I connect to OpenStack
		Then I should be able to delete a networks
