Feature: Manage multiple disks in OpenStack

    Scenario: Delete all "volume_test" volumes
    Given I am connected to OpenStack
    And volumes named "volume_test" exist
    When I delete all volumes named "volume_test"
    Then no volumes named "volume_test" should exist