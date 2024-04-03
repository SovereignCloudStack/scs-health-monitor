# Define security groups
resource "openstack_networking_secgroup_v2" "jump_host_sg" {
  name        = "${var.global_prefix}SG_JumpHost"
  description = "Security Group for Jump Host"
}

# Define rules to allow specific ports
resource "openstack_networking_secgroup_rule_v2" "port22" {
  direction         = "ingress"
  ethertype         = "IPv4"
  security_group_id = openstack_networking_secgroup_v2.jump_host_sg.id
  remote_ip_prefix  = "0.0.0.0/0"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_test" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  port_range_min    = "0"
  port_range_max    = "0"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.jump_host_sg.id
}
