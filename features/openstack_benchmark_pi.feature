@vm
@benchmark
Feature: Benchmark 4000 Pi calculation on VMs

  Scenario Outline: Collect IPs of VMs, access them via SSH, and benchmark Pi calculation
    Given I connect to OpenStack
    And I have a private key at <vm_private_ssh_key_path>
    Then I should be able to collect all VM IPs
    Then I should be able to access <jh_quantity> VMs as user <username>
    Then I should be able to benchmark 4000 digits of Pi on each VM

    Examples:
      | vm_private_ssh_key_path                                                         | username | jh_quantity |
      | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/features/SSH/sshKey | katha    | 3           |
