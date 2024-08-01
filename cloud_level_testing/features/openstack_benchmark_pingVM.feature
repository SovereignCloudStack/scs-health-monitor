@vm
@benchmark
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Given I have deployed <jh_quantity> JHs
    And I have a private key at <keypair_name> for <username>
    Then I should be able to SSH into <jh_quantity> JHs and test their <conn_test> connectivity


    Examples:
	  |jh_name        | keypair_name  | username 	| jh_quantity	| conn_test |
	  |default-jh      | test-keypair-private	  | ubuntu	  | 1	          | ping			|
  #  |localhost      | sshKey	                  | katha			| 1	          | ping			|
