@router
@cleanup
Feature: Delete OpenStack Router

    Scenario Outline: Connect to OpenStack and delete a router
        Given I connect to OpenStack
        When A router with name <router_name> exists
        Then I should be able to delete a router with name <router_name>

        Examples: Test routers
            | router_name |
            | router01    |
            | router02    |
