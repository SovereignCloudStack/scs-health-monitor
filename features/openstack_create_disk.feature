Feature: Manage multiple disks in OpenStack

  Scenario Outline: Create multiple volumes
    Given I connect to OpenStack
    When I create <quantity> volumes

    Examples:
    |quantity|
    |    1   |
