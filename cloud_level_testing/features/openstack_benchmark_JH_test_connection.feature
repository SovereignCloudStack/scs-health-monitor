@ssh
@test
Feature: Test JH connectivity with ping

    Scenario: Test jh connectivity
        Given I have deployed jumphosts with floating ips
        Then I should be able to ping the jumphosts with floating ips
