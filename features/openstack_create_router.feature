@router
@create
Feature: OpenStack Router Creation
  Scenario Outline: Connect to OpenStack and create a routers
    Given I connect to OpenStack
    Then I should be able to create <router_quantity> routers

    Examples:
    |router_quantity|
    |       3       |