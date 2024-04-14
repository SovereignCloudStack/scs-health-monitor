locals {
  security_groups = {
    jump_host_sg = openstack_networking_secgroup_v2.jump_host_sg
    vm_sg        = openstack_networking_secgroup_v2.vm_sg
  }
}

resource "openstack_networking_secgroup_v2" "jump_host_sg" {
  name        = "${var.global_prefix}SG_JumpHost"
  description = "Security Group for Jump Host"
}
resource "openstack_networking_secgroup_v2" "vm_sg" {
  name        = "${var.global_prefix}SG_VM"
  description = "Security Group for VMs"
}

resource "openstack_networking_secgroup_rule_v2" "port22" {
  for_each          = local.security_groups
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  security_group_id = each.value.id
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_test" {
  for_each          = local.security_groups
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  port_range_min    = "0"
  port_range_max    = "0"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = each.value.id
}
