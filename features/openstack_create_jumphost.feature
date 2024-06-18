@jumphost
@create
Feature: OpenStack Jumphost Creation

    Scenario Outline: Connect to OpenStack and create a jumphost
        Given I connect to OpenStack
        Then I create a jumphost with name <jumphost_name> on network <network_name> with keypair <keypair_name>
        Then I attach a floating ip to server <jumphost_name>

  Examples:
<<<<<<< HEAD
    |jumphost_name|   network_name    |keypair_name|
    | default-jh  | scs-hm-jh-default |test-keypair|
    |   test-jh   |  scs-hm-jh-network-1 |sshKey|


=======
    |jumphost_name   |network_name       |keypair_name  |security_group_name|
    | test-jh-katha  |scs-hm-jh-network-1|jhSshKey      |ping-sg            |
#   | test-jh        |scs-hm-jh-network-1|test-keypair  |ping-sg            |
>>>>>>> dependencies in docs  Testflow.md
