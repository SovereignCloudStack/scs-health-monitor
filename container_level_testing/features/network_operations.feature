Feature: Network operations

  Scenario Outline: Pinging another container
    Given a Kubernetes cluster
    And a container named <ping_container>
    And another container named <pong_container>
    When <ping_container> pings <pong_container>
    Then the ping should be successful

  Examples:
    |ping_container|pong_container|
    |ping-container|pong-container|