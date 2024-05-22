@vm
@benchmark
Feature: Test load balancer

  Scenario Outline: Create load balancers and check whether VMs can be reached through their endpoint
    Given I connect to OpenStack
    Then I should be able to create <vms_quantity> VMs



    Examples:
    |vms_quantity|
    | 1          |
