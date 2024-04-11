@security_group
@create
Feature: OpenStack Security Group Creation

  Scenario Outline: Connect to OpenStack and create a security group
    Given I connect to OpenStack
    Then I should be able to create <security_group_quantity> security group

    Examples: Test security groups
      |security_group_quantity|
      |             2         |