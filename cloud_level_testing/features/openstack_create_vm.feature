@vm
@create
Feature: OpenStack Virtual Machine Creation

  Scenario Outline: Connect to OpenStack and create a virtual machine
    Given I connect to OpenStack
    When A security group with name <security_group_name> exists
    Then I should be able to create <vms_quantity> VMs

    Examples:
    |vms_quantity|security_group_name|
    |      1     |ping-sg|
