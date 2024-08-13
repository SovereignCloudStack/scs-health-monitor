Feature: Container management

  Scenario Outline: Creating and deleting a container running a web server
    Given a Kubernetes cluster
    When I create a container named <container_name>
    Then the container <container_name> should be running
    When I create a service for the container named <container_name> on <port>
    Then the service for <container_name> should be running
    When I create a container named <container_name2>
    Then the container <container_name2> should be running
    When I create a service for the container named <container_name2> on <port2>
    Then the service for <container_name2> should be running
    When I send an HTTP request to <container_name> from outside the cluster using node IP node_ip
#    When I send an HTTP request to <container_name>
    Then the response status code should be 200
#    When I send an HTTP request to <container_name2>
#    Then the response status code should be 200
#    When <container_name> pings the service <container_name2>
    Then the ping should be successful
    Then list all containers


  Examples:
    |container_name|port|container_name2|port2|
    |ping-container| 80 |pong-container |  80 |

