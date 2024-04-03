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

variable "image_id" {
  type        = string
  description = "Image for virtual machines"
}

variable "vm_size" {
  type        = number
  description = "Virtual machine size GB"
}

variable "jh_flavor" {
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
