@vm
@cleanup
Feature: OpenStack Virtual Machine Deletion

  Scenario Outline: Connect to OpenStack and delete a virtual machine
    Given I connect to OpenStack
    When A VM with name <vm_name> exists
    Then I should be able to delete the VM with name <vm_name>

    Examples: Test virtual machines
      | vm_name |
      | vm01    |
