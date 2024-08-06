Feature: Deleting ports from a network in OpenStack

  Scenario: Delete all ports from a specific network
    Given I connect to OpenStack
    Then I am able to delete all the ports
