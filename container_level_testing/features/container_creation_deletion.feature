Feature: Container management
  As a user
  I want to manage Kubernetes containers
  So that I can verify they are created, running, and deleted correctly

  @creation
  Scenario Outline: Creating a simple container
    Given a Kubernetes cluster
    When I create a container named <container_name>
    Then the container <container_name> should be running

  Examples:
    | container_name |
    | ping-container |
    | pong-container |

  @networking
  Scenario Outline: Pinging another container
    Given a Kubernetes cluster
    Then the container <src_container> should be running
    Then the container <dst_container> should be running
    When <src_container> pings <dst_container>
    Then the ping should be successful

    Examples:
      | src_container  | dst_container  |
      | ping-container | pong-container |

  @deletion
  Scenario Outline: Deleting a container
    Given a Kubernetes cluster
    Then the container <container_name> should be running
    When I delete the container named <container_name>
    Then the container <container_name> should be deleted

  Examples:
    | container_name |
    | ping-container |
    | pong-container |
