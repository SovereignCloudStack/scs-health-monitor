@vm
@benchmark
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    Given I have deployed a JH with the name <jh_name>
    # TODO:
    # Given I have deployed <jh_quantity> JHs
    and I have a private key at <vm_private_ssh_key_path>
    Then I should be able to SSH into the VM as user <username>
    Then I should be able to collect all VM IPs
    And be able to ping all IPs to test <conn_test> connectivity

    Examples:
	  |jh_name        | vm_private_ssh_key_path   | username 	| jh_quantity	| conn_test |
	  |scs-hm-jh-1    | jh_sshKey-private	        | ubuntu	  | 1	          | ping			|
  #  |localhost      | sshKey	                  | katha			| 1	          | ping			|
