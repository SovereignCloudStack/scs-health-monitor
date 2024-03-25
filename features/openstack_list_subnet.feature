@subnet
@list
Feature: OpenStack Subnet Listing

    Scenario: Connect to OpenStack and list subnets
        Given I connect to OpenStack
        Then I should be able to list subnets
