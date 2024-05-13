Feature: Test creation and deletion of resources

  Scenario Outline: Manage resources in OpenStack
    Given I connect to OpenStack

    Then I should be able to create <router_quantity> routers
    Then I should be able to create <network_quantity> networks
    Then I should be able to create <subnet_quantity> subnets
    Then I should be able to create <security_group_quantity> security groups
    Then I should be able to create <security_group_rules_quantity> security group rules
    Then I create <quantity_volumes> volumes

    Then I should be able to list networks
    Then I should be able to list subnets
    Then I should be able to list routers

    Then I delete all volumes from test
    Then I should be able to delete a security group rules
    Then I should be able to delete a security groups
    Then I should be able to delete subnets
    Then I should be able to delete a networks
    Then I should be able to delete routers

    Examples: Testflow resources
      | router_quantity | network_quantity | subnet_quantity | security_group_quantity | security_group_rules_quantity  | quantity_volumes |
      |        3        |        3         |        2        |            2            |              2                 |        2         |

