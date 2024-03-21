Feature:
  Test creation and deletion resources

  Scenario Outline: Create a router
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    Then I should be able to create a router with name <router_name>
    Examples: Test routers
      | router_name |
      | router01    |
      | router02    |
      | router03    |

  Scenario Outline: Connect to OpenStack and create a network
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    Then I should be able to create a network with name <network_name>

    Examples: Test networks
      | network_name   |
      | network01	   |
      | network02	   |
      | network03	   |

  Scenario Outline: Connect to OpenStack and create a subnet
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    Then I should be able to create a subnet with name <subnet_name> in network <network_name> with <cidr>

    Examples: Test subnets
      | subnet_name | network_name | cidr       |
      | subnet01    | network01    | 10.0.1.0/24|
      | subnet02    | network01    | 10.0.2.0/24|
      | subnet03    | network02    | 10.0.3.0/24|
      | subnet04    | network02    | 10.0.4.0/24|

  Scenario: Connect to OpenStack and list networks
      Given I have the OpenStack environment variables set
      When I connect to OpenStack
      Then I should be able to list networks

  Scenario: Connect to OpenStack and list subnets
        Given I have the OpenStack environment variables set
        When I connect to OpenStack
        Then I should be able to list subnets

  Scenario: Connect to OpenStack and list routers
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    Then I should be able to list routers


  Scenario Outline: Connect to OpenStack and delete a subnet
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    And A subnet with name <subnet_name> exists in network <network_name>
    Then I should be able to delete a subnet with name <subnet_name>

    Examples: Test subnets
      | subnet_name | network_name |
      | subnet01    | network01    |
      | subnet02    | network01    |
      | subnet03    | network02    |
      | subnet04    | network02    |

  Scenario Outline: Connect to OpenStack and delete a network
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    And A network with name <network_name> exists
    Then I should be able to delete a network with name <network_name>

    Examples:Test networks
      | network_name |
      | network01	   |
      | network02	   |
      | network03	   |

  Scenario Outline: Connect to OpenStack and delete a router
    Given I have the OpenStack environment variables set
    When I connect to OpenStack
    And A router with name <router_name> exists
    Then I should be able to delete a router with name <router_name>

    Examples: Test routers
      | router_name |
      | router01    |
      | router02    |
      | router03    |





