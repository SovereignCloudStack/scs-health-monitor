@iperf3
@benchmark
@create
@delete
Feature: Benchmark Iperf3 VMs

  Scenario Outline: Build the benchmark infrastructure used for benchmark tests and perform iperf3
    Given I can get the shared context from previouse feature
    Given I have a private key at <keypair_name> for <username>
    Given I have deployed JHs
    Then I should be able to SSH into VMs and perform <conn_test> test
   
    Examples: Build benchmark infrastructure
    | test_infix | ext_net  | keypair_name          | quantity_vms  | port_start | port_end | username | conn_test |
    | infra      | ext01    | test-keypair          | 2             |      222   | 229      | ubuntu	 | iperf3    |
 