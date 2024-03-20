@subnet
@create
Feature: OpenStack Subnet Creation

    Scenario Outline: Connect to OpenStack and create a subnet
        Given I have the OpenStack environment variables set
        When I connect to OpenStack
        Then I should be able to create a subnet with name <subnet_name> in network <network_name>

        Examples: Test subnets
            | subnet_name | network_name |
            | subnet01    | network01    |
            | subnet02    | network02    |
