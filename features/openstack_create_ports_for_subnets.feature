@network
@create
Feature: OpenStack create ports for subnets
  Scenario: Connect to OpenStack and create a ports for every subnet in test
    Given I connect to OpenStack
    Then I should be able to create port for subnets
