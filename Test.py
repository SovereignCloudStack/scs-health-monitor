import openstack
from openstack.config import loader


def create_connection_from_config():
    return openstack.connect(cloud="gx")

def list_networks(conn):
    print("List Networks:")

    for network in conn.network.networks():
        print(network)

conn = create_connection_from_config()
list_networks(conn)
