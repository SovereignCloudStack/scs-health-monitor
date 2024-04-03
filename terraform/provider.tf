# Define required providers
terraform {
  required_version = ">= 1.5.7"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.54.1"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  region                        = "{region}"
  auth_url                      = "{auth_url}"
  endpoint_type                 = "public"
  application_credential_id     = "{application_credential_id}"
  application_credential_secret = "{application_credential_secret}"
}
