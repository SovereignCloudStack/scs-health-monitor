Feature:
  Test creation and deletion resources

  Scenario Outline: Create a router
    Given I connect to OpenStack
    Then I should be able to create <router_quantity> routers

    Examples: Test routers
      |router_quantity|
      |       3       |

  Scenario Outline: Connect to OpenStack and create a network
    Given I connect to OpenStack
    Then I should be able to create <network_quantity> networks

    Examples: Test networks
      | network_quantity |
      |         3        |

  Scenario Outline: Connect to OpenStack and create a subnet
    Given I connect to OpenStack
    Then I should be able to create a subnet with name <subnet_name> in network <network_name> with <cidr>

    Examples: Test subnets
      |subnet_quantity|
      |      2        |

  Scenario: Connect to OpenStack and list networks
    Given I connect to OpenStack
    Then I should be able to list networks

  Scenario: Connect to OpenStack and list subnets
    Given I connect to OpenStack
    Then I should be able to list subnets

  Scenario: Connect to OpenStack and list routers
    Given I connect to OpenStack
    Then I should be able to list routers

   Scenario Outline: Connect to OpenStack and create a security group
    Given I connect to OpenStack
    Then I should be able to create <security_group_quantity> security groups

    Examples: Test security groups
      |security_group_quantity|
      |             2         |

#  Scenario Outline: Connect to OpenStack and create a security group rule
#    Given I connect to OpenStack
#    Then I should be able to create a security group rule for <security_group_name> with direction <direction> protocol <protocol> and port range <port_range_min> to <port_range_max>
#
#    Examples: Test security groups rule
#      | security_group_name | direction | protocol | port_range_min | port_range_max |
#      | sg01                | ingress   | tcp      | 80             | 120            |

#  Scenario Outline: Connect to OpenStack and delete a security group rule
#    Given I connect to OpenStack
#    When A security group rule for <security_group_name> with direction <direction> protocol <protocol> and port range <port_range_min> to <port_range_max> exists
#    Then I should be able to delete the security group rule for <security_group_name> with direction <direction> protocol <protocol> and port range <port_range_min> to <port_range_max>
#
#    Examples: Test security groups rule
#      | security_group_name | direction | protocol | port_range_min | port_range_max |
#      | sg01                | ingress   | tcp      | 81             | 119            |

  Scenario: Connect to OpenStack and delete a security groups

    Given I connect to OpenStack
    Then I should be able to delete a security groups



  Scenario Outline: Connect to OpenStack and delete a network
    Given I connect to OpenStack
    When A network with name <network_name> exists
    Then I should be able to delete a network with name <network_name>

    Examples:Test networks
      | network_name |
      | network01    |
      | network02    |
      | network03    |

  Scenario Outline: Connect to OpenStack and delete a router
    Given I connect to OpenStack
    When A router with name <router_name> exists
    Then I should be able to delete a router with name <router_name>

    Examples: Test routers
      | router_name |
      | router01    |
      | router02    |
      | router03    |





