@vm
@benchmark
Feature: Benchmark ping VMs

  Scenario Outline: Collecting IPs of VMs can be reached through Openstack, ping them from remote accesses and track retries and failures
    Given I connect to OpenStack
    #Given I have deployed a JH with the name <jh_name>
    # TODO:
    Given I have deployed <jh_quantity> JHs
    and I have a private key at <vm_private_ssh_key_path> for <username>
#    Then I should be able to SSH into <jh_quantity> JHs and test their <conn_test> connectivity
    Then I should be able to SSH into the VM
    Then I should be able to collect all VM IPs
    And be able to ping all IPs to test <conn_test> connectivity

    Examples:
	  |jh_name        | vm_private_ssh_key_path   | username 	| jh_quantity	| conn_test |
	  |scs-hm-jh      | create_keypair-private	  | ubuntu	  | 4	          | ping			|
  #  |localhost      | sshKey	                  | katha			| 1	          | ping			|
