@subnet
@cleanup
Feature: OpenStack Subnet Deletion

  Scenario: Connect to OpenStack and delete a subnet
    Given I connect to OpenStack
    Then I should be able to delete subnets

