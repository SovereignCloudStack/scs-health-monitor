@router
@list
Feature: OpenStack Router Listing

    Scenario: Connect to OpenStack and list routers
        Given I connect to OpenStack
        Then I should be able to list routers
