data "openstack_networking_network_v2" "external_network" {
  network_id = var.external_network_id
}

resource "openstack_networking_network_v2" "network_1" {
  name           = "${var.global_prefix}network"
  admin_state_up = "true"
}

resource "openstack_networking_router_v2" "router_1" {
  name                = "${var.global_prefix}router"
  admin_state_up      = true
  external_network_id = var.external_network_id
}

resource "openstack_networking_subnet_v2" "subnet_1" {
  name       = "${var.global_prefix}subnet"
  network_id = openstack_networking_network_v2.network_1.id
  cidr       = var.subnet_cidr
  ip_version = 4
}

resource "openstack_networking_port_v2" "jump_host_port" {
  name               = "${var.global_prefix}Port_JH"
  security_group_ids = [openstack_networking_secgroup_v2.jump_host_sg.id]
  network_id         = openstack_networking_network_v2.network_1.id
  fixed_ip {
    ip_address = var.jh_fixed_ip
    subnet_id  = openstack_networking_subnet_v2.subnet_1.id
  }
  # # Specify allowed address pairs
  # allowed_address_pairs {
  #   ip_address = "0.0.0.0/1"
  # }
  # allowed_address_pairs {
  #   ip_address = "128.0.0.0/1"
  # }
}

# Plug multiple subnets into router
resource "openstack_networking_router_interface_v2" "subnets" {
  router_id = openstack_networking_router_v2.router_1.id
  subnet_id = openstack_networking_subnet_v2.subnet_1.id
}

resource "openstack_networking_floatingip_v2" "fips" {
  pool        = data.openstack_networking_network_v2.external_network.name
  description = "${var.global_prefix}JH"
  port_id     = openstack_networking_port_v2.jump_host_port.id
}
