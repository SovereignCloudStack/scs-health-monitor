@security_group_rule
@cleanup
Feature: Delete OpenStack Security Group Rule

  Scenario Outline: Connect to OpenStack and delete a security group rule
    Given I connect to OpenStack
    Then I should be able to delete a security group rule with direction <direction>

    Examples: Test security groups rule
      | direction | 
      | ingress   | 
      | egress    | 
