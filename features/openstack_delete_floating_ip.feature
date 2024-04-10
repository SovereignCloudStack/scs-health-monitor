@network
@create
Feature: OpenStack floating ip deletion

  Scenario Outline: Connect to OpenStack and create a floating ip
    Given I connect to OpenStack
    Then I should be able to delete all floating ip with

    Examples:


