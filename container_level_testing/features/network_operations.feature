Feature: Network operations

  Scenario: Pinging another container
    Given a Kubernetes cluster
    And a container named "ping-container"
    And another container named "pong-container"
    When "ping-container" pings "pong-container"
    Then the ping should be successful