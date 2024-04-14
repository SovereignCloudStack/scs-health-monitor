variable "global_prefix" {
  type        = string
  description = "Default prefix"
}

variable "external_network_id" {
  type        = string
  description = "External network ID"
}

variable "availability_zone" {
  type        = string
  description = "Availability zone"
}

variable "JH_image_id" {
  type        = string
  description = "Image for virtual machines"
}

variable "JH_size" {
  type        = number
  description = "Virtual machine size GB"
}

variable "JH_flavor" {
  type        = string
  description = "Instance flavor for JH VM"
}

variable "subnet_cidr" {
  type        = string
  description = "Subnet cidr for JH VM"
}

variable "jh_fixed_ip" {
  type        = string
  description = "IP for JH"
}

variable "region" {
  type        = string
  description = "Region in openstack"
  default     = "RegionOne"
}

variable "auth_url" {
  type        = string
  description = "Openstack auth URL"
}

variable "application_credential_id" {
  type        = string
  description = "Openstack application credential ID"
}

variable "application_credential_secret" {
  type        = string
  description = "Openstack application credential secret"
}

variable "VM_networks_count" {
  type        = number
  description = "Number of networks to create for VMs"
}

variable "VM_subnet_base_prefix" {
  type        = string
  description = "Base address space for VM subnet"
  default     = "10.0.0.0/16"
}

variable "VM_count" {
  type        = number
  description = "Number of normal VMs to create. These vms will be distributed evenly between the subnets"
  default     = 2
}

variable "VM_image_id" {
  type        = string
  description = "Image for virtual machines"
}

variable "VM_size" {
  type        = number
  description = "Virtual machine size GB"
}

variable "VM_flavor" {
  type        = string
  description = "Instance flavor for JH VM"
}
