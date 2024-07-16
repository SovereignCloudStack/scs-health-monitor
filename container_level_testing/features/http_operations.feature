Feature: HTTP operations

  Scenario: HTTP request to a container
    Given a Kubernetes cluster
    And a container running a web server named "web-container"
    When I send an HTTP request to "web-container"
    Then the response status code should be 200