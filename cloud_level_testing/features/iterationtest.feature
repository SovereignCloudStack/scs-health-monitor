Feature: i want <quantity> iterations
  Scenario Outline: Example scenario
    Given I want to test iterations
    Then iterate steps <quantity> times
  
    Examples:
    |quantity|
    |3|