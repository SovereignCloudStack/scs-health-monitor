Feature: Delete openstack network

	Scenario: Connect to OpenStack and delete a network
		Given I have the OpenStack environment variables set
		When I connect to OpenStack
		And A network with name test01 exists
		Then I should be able to delete a network with name test01