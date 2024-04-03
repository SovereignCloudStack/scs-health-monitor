output "JH_IP" {
  value       = openstack_networking_floatingip_v2.fips.address
  description = "Public IP of the JH server"
}
