@loadbalancer
@benchmark
Feature: Benchmark loadbalancer

  Scenario Outline: Create load balancers and check whether VMs can be reached through their endpoint
#    Then I should be able to create a loadbalancer
    #Then I should be able to create loadbalancer listeners
    #Then I should be able to create loadbalancer pools
    #Then I should be able to create loadbalancer members
    #Then I should be able to access VMs through loadbalancers

    # Kill some backends
    #When I kill the backend of load balancer members
    #Then the load balancer pool should have degraded members
    #Then I should be able to access VMs through loadbalancers

    Examples: Build benchmark loadbalancer
    | test_prefix | ext_net | keypair_name |
    | infra           |    ext01    |    tf-id-rsa      |

    # openstack loadbalancer create --name lb1 --vip-subnet-id public-subnet --wait
    # openstack loadbalancer listener create --name listener1 --protocol HTTP --protocol-port 80 --wait lb1
    # openstack loadbalancer pool create --name pool1 --lb-algorithm ROUND_ROBIN --listener listener1 --protocol HTTP --wait
    # openstack loadbalancer member create --subnet-id private-subnet --address 192.0.2.10 --protocol-port 80 --wait pool1
    # openstack loadbalancer member create --subnet-id private-subnet --address 192.0.2.11 --protocol-port 80 --wait pool1
