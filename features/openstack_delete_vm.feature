@vm
@cleanup
Feature: OpenStack Virtual Machine Deletion

  Scenario: Connect to OpenStack and delete a virtual machine
    Given I connect to OpenStack
    Then I should be able to delete the VMs