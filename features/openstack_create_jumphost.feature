Feature: OpenStack Jumphost Creation

	Scenario Outline: Connect to OpenStack and create a jumphost
		Given I have the OpenStack environment variables set
		When I connect to OpenStack
		Then I should be able to create a jumphost with name <jumphost_name>

		Examples: Test jumphost
			| jumphost_name |
			| test02	    |
			| test03	    |