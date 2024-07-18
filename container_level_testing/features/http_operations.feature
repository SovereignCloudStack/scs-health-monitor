Feature: HTTP operations

  Scenario Outline: HTTP request to a container
    Given a Kubernetes cluster
    And a container running a web server named <container_name>
    When I send an HTTP request to <container_name>
    Then the response status code should be 200

    Examples:
    |container_name|

    |web-server|