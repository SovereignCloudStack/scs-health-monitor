Feature: Container management
  As a user
  I want to manage Kubernetes containers
  So that I can verify they are created, running, and deleted correctly

  Scenario Outline: Deleting a container
    Given a Kubernetes cluster
    Then the container <container_name> should be running
    When I delete the container named <container_name>
    Then the container <container_name> should be deleted

  Examples:
    |container_name|
    |ping-container|
    |pong-container|
#    |web-server|