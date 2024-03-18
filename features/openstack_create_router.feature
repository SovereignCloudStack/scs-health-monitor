@router
@create
Feature: OpenStack Router Creation

    Scenario Outline: Connect to OpenStack and create a router
        Given I have the OpenStack environment variables set
        When I connect to OpenStack
        Then I should be able to create a router with name <router_name>

        Examples: Test routers
            | router_name |
            | router01    |
            | router02    |
