@subnet
@cleanup
Feature: OpenStack Subnet Deletion

    Scenario Outline: Connect to OpenStack and delete a subnet
        Given I have the OpenStack environment variables set
        When I connect to OpenStack
        And A subnet with name <subnet_name> exists in network <network_name>
        Then I should be able to delete a subnet with name <subnet_name>

        Examples: Test subnets
            | subnet_name | network_name |
            | subnet01    | network01    |
            | subnet02    | network02    |
