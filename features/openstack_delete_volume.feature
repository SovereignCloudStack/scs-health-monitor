Feature: Delete volumes used in tests
  Scenario: Delete all volumes created in test
    Given I connect to OpenStack
    Then I delete all volumes from test