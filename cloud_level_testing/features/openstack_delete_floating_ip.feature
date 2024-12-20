@network
@create
Feature: OpenStack floating ip deletion

  Scenario Outline: Connect to OpenStack and create and delete a plain floating ip
    Given I connect to OpenStack
    Then I should be able to create a plain floating ip which is not associated to something
    Then I should be able to delete all previously created plain floating ips
