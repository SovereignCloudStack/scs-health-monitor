@security_group
@cleanup
Feature: Delete OpenStack Security Group

    Scenario Outline: Connect to OpenStack and delete a security group

        Given I connect to OpenStack
        When A security group with name <security_group_name> exists
        Then I should be able to delete a security group with name <security_group_name>

        Examples: Test security groups
            | security_group_name |
            | sg01                |
            | sg02                |