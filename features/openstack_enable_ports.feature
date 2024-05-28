@network
@create
Feature: OpenStack enable ports for networks
  Scenario: Connect to OpenStack and enable a ports for every subnet in test
    Given I connect to OpenStack
    Then I enable all ports in all networks
