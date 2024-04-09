Feature: OpenStack Availability zones creation

  Scenario Outline: Connect to OpenStack and create an availability zone
    Given I connect to OpenStack
  	Then I should be able to create an <availability_zone>

    Examples: Test availability zone
      | availability_zone     |
      | availabilityzone01	    |
      | availabilityzone02	    |