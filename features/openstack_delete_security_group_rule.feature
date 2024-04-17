@security_group_rule
@cleanup
Feature: Delete OpenStack Security Group Rule

  Scenario Outline: Connect to OpenStack and delete a security group rule
    Given I connect to OpenStack
    Then I should be able to delete a security group rule with direction <direction> protocol <protocol> and port range <port_range_min> to <port_range_max>

    Examples: Test security groups rule
      | direction | protocol | port_range_min | port_range_max |
      | ingress   | tcp      | 80             | 80             |
