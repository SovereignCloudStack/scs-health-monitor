# Jumphost connection

1) You need to run `openstack_create_jumphost.feature` first, which sets up the jumphost in openstack and creates private ssh access key locally (name of ssh key, network and jumphost can be edited in the feature file):

    `behave features/openstack_create_jumphost.feature`

2) After the feature run successfully passes, you need to get the public ip address of the jumphost by running `openstack server list` and reading it from the output for the desired jumphost under `networks` column.

3) Aleternatively, you can run `openstack server show <jumphost_name>` and read the ip value under `addresses`.

4) Finally, you can connect to the jumphost with command:

    `ssh -i <private_key_filename> ubuntu@<jumphost_ip_address>`

# Floating ip

We are currently unable to create our own floating IPs. The working solution for now is to take the IP for jumphost from the list of available floating IPs. We used `add_auto_ip` [function][function_link], which automatically assigns available floating IP from the pool.

[function_link]: https://docs.openstack.org/openstacksdk/latest/user/connection.html#openstack.connection.Connection.add_auto_ip