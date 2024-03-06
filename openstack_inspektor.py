from neutronclient.v2_0 import client as neutronclient
import yaml

class Inspector:

    def __init__(self, env_file_path="env.yaml"):
        self.env_file_path = env_file_path
        self.env = self.load_env_from_yaml()
        self.neutron = self.create_neutron_client()

    def load_env_from_yaml(self):
        with open(self.env_file_path, 'r') as file:
            env = yaml.safe_load(file)
        return env

    def create_neutron_client(self):
        #TODO: add a different, more general client to connect to services
        return neutronclient.Client(
            auth_url=self.env["OS_AUTH_URL"],
            token=self.env["OS_APPLICATION_CREDENTIAL_ID"],
            token_secret=self.env["OS_APPLICATION_CREDENTIAL_SECRET"],
            project_name=self.env["OS_PROJECT_NAME"],
            user_domain_name=self.env["OS_USER_DOMAIN_NAME"],
            project_domain_name=self.env["OS_PROJECT_DOMAIN_NAME"]
        )

    def check_network_existence(self, network_name):
        #TODO: use the client to connect to nova networking service
        try:
            networks = self.neutron.list_networks()["networks"]
            for net in networks:
                if net['name'] == network_name:
                    return True
        except Exception as e:
            print(f"Error while checking network existence: {e}")
        return False


# Example usage:
inspector = Inspector()
if inspector.check_network_existence("ext01"):
    print("Network exists!")
else:
    print("Network does not exist.")
