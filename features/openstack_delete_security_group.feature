@security_group
@cleanup
Feature: Delete OpenStack security groups

  Scenario: Connect to OpenStack and delete a security groups

    Given I connect to OpenStack
    Then I should be able to delete a security groups
