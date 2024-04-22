Feature: Create disk from image in OpenStack

  Scenario Outline: Create a disk from an image
    Given I connect to OpenStack
    Then I create <quantity_volumes> volumes

  Examples:
    |quantity_volumes|
    |    2   |