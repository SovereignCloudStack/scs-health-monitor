@network
@create
Feature: OpenStack disable ports for networks
  Scenario: Connect to OpenStack and enable a ports for every subnet in test
    Given I connect to OpenStack
    Then I disable all ports in all networks

