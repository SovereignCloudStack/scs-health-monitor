@vm
@create
Feature: OpenStack Virtual Machine Creation

  Scenario Outline: Connect to OpenStack and create a virtual machine
    Given I connect to OpenStack
    Then I should be able to create a VM with name <vm_name> using image <image_name> and flavor <flavor_name> on network <network_name>

    Examples: Test virtual machines
      | vm_name | image_name   | flavor_name | network_name |
      | vm01    | Ubuntu 20.04 | SCS-1V:1:10 | network01    |