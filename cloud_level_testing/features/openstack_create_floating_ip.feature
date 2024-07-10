@network
@create
Feature: OpenStack floating ip reation
  Scenario Outline: Connect to OpenStack and create a floating ip
    Given I connect to OpenStack
    Then I should be able to create a floating ip on <subnet>, on <server>, with <fixed_address>, for <nat_destination> on <port>

    Examples: Test networks
      | subnet |
      | subnet01	   |
      | subnet02	   |