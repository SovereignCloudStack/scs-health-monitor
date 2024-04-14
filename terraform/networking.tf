data "openstack_networking_network_v2" "external_network" {
  network_id = var.external_network_id
}

resource "openstack_networking_network_v2" "network_1" {
  name           = "${var.global_prefix}JH-network"
  admin_state_up = "true"
}

resource "openstack_networking_router_v2" "router_1" {
  name                = "${var.global_prefix}router"
  admin_state_up      = true
  external_network_id = var.external_network_id
}

resource "openstack_networking_subnet_v2" "subnet_1" {
  name       = "${var.global_prefix}JH-subnet"
  network_id = openstack_networking_network_v2.network_1.id
  cidr       = var.subnet_cidr
  ip_version = 4
}

resource "openstack_networking_port_v2" "jump_host_port" {
  name               = "${var.global_prefix}JH-Port"
  security_group_ids = [openstack_networking_secgroup_v2.jump_host_sg.id]
  network_id         = openstack_networking_network_v2.network_1.id
  fixed_ip {
    ip_address = var.jh_fixed_ip
    subnet_id  = openstack_networking_subnet_v2.subnet_1.id
  }
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

# Data Block for Availability Zones
data "openstack_compute_availability_zones_v2" "azs" {
  # Optionally, you can filter the availability zones here
}

# Resources
resource "openstack_networking_network_v2" "VM_networks" {
  count = var.VM_networks_count
  name  = "${var.global_prefix}VM-network-${count.index + 1}"

  availability_zone_hints = [element(data.openstack_compute_availability_zones_v2.azs.names, count.index % length(data.openstack_compute_availability_zones_v2.azs.names))]
}

resource "openstack_networking_subnet_v2" "VM_subnets" {
  count      = var.VM_networks_count
  name       = "${var.global_prefix}VM-subnet-${count.index + 1}"
  network_id = openstack_networking_network_v2.VM_networks[count.index].id
  cidr       = cidrsubnet(var.VM_subnet_base_prefix, 8, (count.index + 1) * 5)
  ip_version = 4
}

# Plug multiple subnets into router
resource "openstack_networking_router_interface_v2" "VM_subnets" {
  count     = var.VM_networks_count
  router_id = openstack_networking_router_v2.router_1.id
  subnet_id = openstack_networking_subnet_v2.VM_subnets[count.index].id
}

resource "openstack_networking_port_v2" "vm_host_port" {
  count              = var.VM_count
  name               = "${var.global_prefix}Port_VM-${count.index + 1}"
  security_group_ids = [openstack_networking_secgroup_v2.vm_sg.id]
  network_id         = openstack_networking_network_v2.VM_networks[count.index % length(openstack_networking_network_v2.VM_networks)].id
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.VM_subnets[count.index % length(openstack_networking_subnet_v2.VM_subnets)].id
  }
}
