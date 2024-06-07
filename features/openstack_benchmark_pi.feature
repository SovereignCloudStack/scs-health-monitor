@vm
@benchmark
Feature: Benchmark 4000 Pi calculation on VMs

  Scenario Outline: Collect IPs of VMs, access them via SSH, and benchmark Pi calculation
    Given I connect to OpenStack
    Given I have deployed a VM with IP <vm_ip_address>
    And I have a private key at <vm_private_ssh_key_path>
    Then I should be able to SSH into the VM as user <username>
    Then I should be able to collect all VM IPs
    Then I should be able to calculate 4000 digits of Pi on each VM and measure time

    Examples:
      | vm_ip_address   | vm_private_ssh_key_path                                                               | username | jh_quantity |
      | 213.131.230.157 | /home/katha/Dokumente/WORKLOAD_LOCAL/SCS/scs-health-monitor/terraform/private_key.pem | ubuntu   | 3           |