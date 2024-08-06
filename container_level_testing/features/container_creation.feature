Feature: Container creation

  Scenario Outline: Creating a simple container
    Given a Kubernetes cluster
    When I create a container named <container_name>
    Then the container <container_name> should be running

  Examples:
    |container_name|
    |test-container|
    |web-server|