@jumphost
@create
Feature: OpenStack Jumphost Creation

    Scenario Outline: Connect to OpenStack and create a jumphost
        Given I connect to OpenStack
        When A security group with name <security_group_name> exists
        Then I create a jumphost with name <jumphost_name> on network <network_name> with keypair <keypair_name>
        Then I attach a floating ip to server <jumphost_name>

  Examples:
    |jumphost_name|network_name    |keypair_name|security_group_name|
    |    test-scs-3  |scs-hm-network-1|test-keypair-3|ping-sg|