@iperf3
@benchmark
Feature: Benchmark Iperf3 VMs

  Scenario Outline: Build the benchmark infrastructure used for benchmark tests and perform iperf3
    Given I can get the shared context from previouse feature
    Given I have a private key at <keypair_name> for <username>
    Given I have deployed JHs
    Then I should be able to SSH into VMs and perform <conn_test> test
   
    Examples: Build benchmark infrastructure
    | keypair_name          | username  | conn_test |
    | test-keypair          | ubuntu    | iperf3    |
