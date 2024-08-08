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
    | test_infix | ext_net  | keypair_name   | quantity_vms  | port_start | port_end | username | conn_test |
    | infra      | ext01    | test-keypair   | 2             |      222   | 229      | ubuntu	  | ping			|
 