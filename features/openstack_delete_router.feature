@router
@cleanup
Feature: Delete OpenStack Router

  Scenario: Connect to OpenStack and delete a router
    Given I connect to OpenStack
    Then I should be able to delete routers
