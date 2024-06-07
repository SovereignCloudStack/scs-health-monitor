@virtual_machine
@create

Feature: VM Creation Testing

    Scenario Outline: Create VM in OpenStack
        Given I connect to OpenStack
        Then I create an access jumphost with name <jumphost_name> on network <network_name> with keypair <keypair_name>
        Then I attach a floating ip <floating_ip> to server <jumphost_name>

  Examples:
    |jumphost_name|network_name|keypair_name|floating_ip|
    |    test-jh  |scs-hm-network-1|test-keypair|'213.131.230.205'|
