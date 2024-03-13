import openstack
import yaml
from libs.loggerClass import Logger


class Inspector:
    def __init__(self, env_file_path="env.yaml"):
        self.log = Logger(name="inspector_logger", log_file="logfile.log")
        self.logger_instance = self.log.instance
        self.env_file_path = env_file_path
        self.env = self.load_env_from_yaml()
        self.client = openstack.connect(cloud="gx")

    def load_env_from_yaml(self):
        with open(self.env_file_path, "r") as file:
            env = yaml.safe_load(file)
            self.logger_instance.debug("success:found environment variables")
        return env

    def check_network_existence(self, network_name):
        try:
            networks = self.client.network.networks()
            for net in networks:
                if net["name"] == network_name:
                    self.logger_instance.info(f"Network found: {network_name}")
                    return True
                else:
                    continue
        except Exception as e:
            self.logger_instance.error(f"Error while checking network existence: {e}")


# Example usage:
if __name__ == "__main__":

    inspector = Inspector()
    if inspector.check_network_existence("ext01"):
        print("Network exists!")
    else:
        print("Network does not exist.")
