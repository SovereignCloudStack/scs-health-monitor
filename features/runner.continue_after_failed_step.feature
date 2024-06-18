@runner.continue_after_failed_step 
Feature: Test creation and deletion of resources

  Scenario Outline: Manage resources in OpenStack
    Given I connect to OpenStack

    Then I should be able to list routers
    Then I should be able to list networks
    Then I should be able to list subnets

    Then I delete all volumes from test
    Then I should be able to delete a security group rules
    Then I should be able to delete a security groups
    Then I should be able to delete subnets
    Then I should be able to delete a networks
    Then I should be able to delete routers


