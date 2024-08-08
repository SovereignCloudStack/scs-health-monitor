@vm
@benchmark
@create
@delete
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures   
    Given I can get the shared context from previouse feature
    Given I have deployed JHs
    And I have a private key at <keypair_name> for <username>
    Then I should be able to SSH into JHs and test their <conn_test> connectivity
    Examples: Build benchmark infrastructure
    | keypair_name   | username | conn_test |
    | test-keypair   | ubuntu	  | ping			|
 