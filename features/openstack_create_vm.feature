@vm
@create
Feature: OpenStack Virtual Machine Creation

  Scenario Outline: Connect to OpenStack and create a virtual machine
    Given I connect to OpenStack
    Then I should be able to create <vms_quantity> VMs

    Examples:
    |vms_quantity|
    | 1          |
