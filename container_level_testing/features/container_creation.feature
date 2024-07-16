Feature: Container creation

  Scenario Outline: Creating a simple container
    Given a Kubernetes cluster
    When I create a container named <test-container>
    Then the container <test-container> should be running

  Examples:
    |name|
    |    test-container|
