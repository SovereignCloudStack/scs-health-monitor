Feature: Test creation and deletion of resources

  Scenario Outline: Manage resources in OpenStack
    Given I connect to OpenStack

    Then I should be able to create <router_quantity> routers
    And I should be able to create <network_quantity> networks
    And I should be able to create <subnet_quantity> subnets
    And I should be able to create <security_group_quantity> security groups
    And I create <quantity_volumes> volumes

    Then I should be able to list networks
    And I should be able to list subnets
    And I should be able to list routers

    Then I delete all volumes from test
    And I should be able to delete a security groups
    And I should be able to delete subnets
    And I should be able to delete a networks
    And I should be able to delete routers

    Examples: Testflow resources
      | router_quantity | network_quantity | subnet_quantity | security_group_quantity | quantity_volumes |
      |        3        |        3         |        2        |            2            |        2         |
