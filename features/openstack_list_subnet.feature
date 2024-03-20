@subnet
@list
Feature: OpenStack Subnet Listing

    Scenario: Connect to OpenStack and list subnets
        Given I have the OpenStack environment variables set
        When I connect to OpenStack
        Then I should be able to list subnets
