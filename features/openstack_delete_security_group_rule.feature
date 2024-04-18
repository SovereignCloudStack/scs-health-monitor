@security_group_rule
@cleanup
Feature: Delete OpenStack Security Group Rule

  Scenario: Connect to OpenStack and delete a security group rule
    Given I connect to OpenStack
    Then I should be able to delete a security group rules
