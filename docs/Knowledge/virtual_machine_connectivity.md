# Jumphost connection

1) You need to run `openstack_create_jumphost.feature` first, which sets up the jumphost in openstack and creates private ssh access key locally (name of ssh key, network and jumphost can be edited in the feature file):

    `behave cloud_level_testing/features/openstack_create_jumphost.feature`

2) After the feature run successfully passes, you need to get the public ip address of the jumphost by running `openstack server list` and reading it from the output for the desired jumphost under `networks` column.

3) Alternatively, you can run `openstack server show <jumphost_name>` and read the ip value under `addresses`.

4) Finally, you can connect to the jumphost with command:

    `ssh -i <private_key_filename> ubuntu@<jumphost_ip_address>`

# Floating ip

We are creating new floating IP address in the pool each time for the newly created jumphost servers. We used `add_auto_ip` [function][function_link], which automatically creates and attaches a floating IP to the created server. Created floating IP IDs are collected in our `collector` object, which gathers all test related resources, and these are deleted after each test run.

[function_link]: https://docs.openstack.org/openstacksdk/latest/user/connection.html#openstack.connection.Connection.add_auto_ip