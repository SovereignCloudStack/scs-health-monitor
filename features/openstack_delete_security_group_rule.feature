@security_group_rule
@cleanup
Feature: Delete OpenStack Security Group Rule

    Scenario Outline: Connect to OpenStack and delete a security group rule
        Given I connect to OpenStack
        When A security group rule for <security_group_name> with direction <direction> protocol <protocol> and port range <port_range_min> to <port_range_max> exists
        Then I should be able to delete the security group rule for <security_group_name> with direction <direction> protocol <protocol> and port range <port_range_min> to <port_range_max>

        Examples: Test security groups rule
            | security_group_name | direction | protocol | port_range_min | port_range_max |
            | sg01                | ingress   | tcp      | 80             | 80             |
