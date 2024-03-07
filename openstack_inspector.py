import openstack
import yaml

class Inspector:

    def __init__(self, env_file_path="env.yaml"):
        self.env_file_path = env_file_path
        self.env = self.load_env_from_yaml()
        self.client = openstack.connect(cloud="gx")

    def load_env_from_yaml(self):
        with open(self.env_file_path, 'r') as file:
            env = yaml.safe_load(file)
        return env

    def check_network_existence(self, network_name):
        try:
            networks = self.client.network.networks()
            for net in networks:
                if net["name"] == network_name:
                    return True
                else: continue
            #TODO: log all of the networks to logfile
        except Exception as e:
            print(f"Error while checking network existence: {e}")


# Example usage:
inspector = Inspector()
if inspector.check_network_existence("ext01"):
    print("Network exists!")
else:
    print("Network does not exist.")
