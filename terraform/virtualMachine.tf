resource "openstack_compute_keypair_v2" "jump_host_keypair" {
  name = "${var.global_prefix}JH-keypair"
}

resource "openstack_blockstorage_volume_v3" "jump_host_volume" {
  availability_zone = var.availability_zone
  name              = "${var.global_prefix}RootVolume_JH"
  image_id          = var.image_id
  size              = var.vm_size
}

resource "openstack_compute_instance_v2" "jump_host_vms" {
  name              = "${var.global_prefix}VM_JH"
  flavor_name       = var.jh_flavor
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
    volume_size      = var.vm_size
  }

  #   user_data = "base64_encoded_cloud_init_content_here"
}

resource "local_file" "private_key" {
  content  = openstack_compute_keypair_v2.jump_host_keypair.private_key
  filename = "private_key.pem"
}
