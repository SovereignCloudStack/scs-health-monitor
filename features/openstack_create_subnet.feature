@subnet
@create
Feature: OpenStack Subnet Creation

  Scenario Outline: Connect to OpenStack and create a subnet
    Given I connect to OpenStack
    Then I should be able to create <subnet_quantity> subnets

    Examples: Test subnets
      |subnet_quantity|
      |       2       |
