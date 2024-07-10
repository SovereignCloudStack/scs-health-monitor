Feature: OpenStack Jumphost Deletion

	Scenario Outline: Connect to OpenStack and delete a jumphost
		Given I connect to OpenStack
		Then I should be able to delete a jumphost with name <jumphost_name>

		Examples: Test jumphost
			| jumphost_name |
			| test02	    |
			| test03	    |