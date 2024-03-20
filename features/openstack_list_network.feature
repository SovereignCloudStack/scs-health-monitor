@network
Feature: OpenStack Network Listing

	Scenario: Connect to OpenStack and list networks
		Given I have the OpenStack environment variables set
		When I connect to OpenStack
		Then I should be able to list networks