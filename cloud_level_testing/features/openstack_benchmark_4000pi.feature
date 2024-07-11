@vm
@benchmark
Feature: Test VM under load

  Scenario Outline: Test VM response time while under load (calculating 4000 digits of pi)
    Given I connect to OpenStack
    Given I have a private key at <vm_private_ssh_key_path> for <username>
    Then I create a jumphost with name <jumphost_name> on network <network_name> with keypair <keypair_name>
    Then I attach a floating ip to server <jumphost_name>   
    Then I should be able to SSH into the VM
    Then I start calculating 4000 digits of pi on VM and check the ping response

  Examples:
    |jumphost_name|   network_name    |keypair_name| username |vm_private_ssh_key_path|
    |  test-jh-1  | scs-hm-jh-default |test-keypair|  ubuntu  |test-keypair-private|