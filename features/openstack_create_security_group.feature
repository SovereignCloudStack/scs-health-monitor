@security_group
@create
Feature: OpenStack Security Group Creation

  Scenario Outline: Connect to OpenStack and create a security group
    Given I connect to OpenStack
    Then I should be able to create a security group with name <security_group_name> with <description>

    Examples: Test security groups
      | security_group_name | description       |
      | sg01                | "First group"     |
      | sg02                | "Second group"    |