resource "openstack_compute_keypair_v2" "jump_host_keypair" {
  name = "${var.global_prefix}JH-keypair"
}

resource "openstack_blockstorage_volume_v3" "jump_host_volume" {
  availability_zone = var.availability_zone
  name              = "${var.global_prefix}RootVolume_JH"
  image_id          = var.JH_image_id
  size              = var.JH_size
}

resource "openstack_compute_instance_v2" "jump_host_vms" {
  name              = "${var.global_prefix}VM_JH"
  flavor_name       = var.JH_flavor
  key_pair          = openstack_compute_keypair_v2.jump_host_keypair.name
  availability_zone = var.availability_zone
  security_groups   = [openstack_networking_secgroup_v2.jump_host_sg.name]
  network {
    port = openstack_networking_port_v2.jump_host_port.id
  }

  user_data = file("./jh_init.sh")

  block_device {
    uuid             = openstack_blockstorage_volume_v3.jump_host_volume.id
    source_type      = "volume"
    destination_type = "volume"
    boot_index       = 0
    volume_size      = var.JH_size
  }

  #   user_data = "base64_encoded_cloud_init_content_here"
}

resource "local_file" "private_key" {
  content  = openstack_compute_keypair_v2.jump_host_keypair.private_key
  filename = "private_key.pem"
}

resource "openstack_blockstorage_volume_v3" "vm_volumes" {
  count             = var.VM_count
  availability_zone = var.availability_zone
  name              = "${var.global_prefix}RootVolume-VM-${count.index + 1}"
  image_id          = var.VM_image_id
  size              = var.VM_size
}

resource "openstack_compute_instance_v2" "vms" {
  count       = var.VM_count
  name        = "${var.global_prefix}VM-${count.index + 1}"
  flavor_name = var.VM_flavor
  key_pair    = openstack_compute_keypair_v2.jump_host_keypair.name

  availability_zone = element(data.openstack_compute_availability_zones_v2.azs.names, count.index % length(data.openstack_compute_availability_zones_v2.azs.names))
  security_groups   = [openstack_networking_secgroup_v2.vm_sg.name]

  network {
    port = openstack_networking_port_v2.vm_host_port[count.index].id
  }

  block_device {
    uuid             = openstack_blockstorage_volume_v3.vm_volumes[count.index].id
    source_type      = "volume"
    destination_type = "volume"
    boot_index       = 0
    volume_size      = var.VM_size
  }

  #   user_data = "base64_encoded_cloud_init_content_here"
}
