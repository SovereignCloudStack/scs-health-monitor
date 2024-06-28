@vm
@benchmark
Feature: Test VM under load

  Scenario Outline: Test VM response time while under load (calculating 4000 digits of pi)
    Given I connect to OpenStack
    Given I have a private key at <vm_private_ssh_key_path>
    Then I create a jumphost with name <jumphost_name> on network <network_name> with keypair <keypair_name>
    Then I attach a floating ip to server <jumphost_name>
    Then I should be able to SSH into the VM as user <username>

  Examples:
    |jumphost_name|   network_name    |keypair_name| username |vm_private_ssh_key_path|
    |  test-jh-1  | scs-hm-jh-default |test-keypair|  ubuntu  |/home/tsmado/vp12/scs-health-monitor/test-keypair-private|