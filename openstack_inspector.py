import openstack
import yaml
from libs.loggerClass import Logger

class Inspector:
    def __init__(self, env_file_path="env.yaml"):
        self.env_file_path = env_file_path
        self.env = self.load_env_from_yaml()
        self.client = openstack.connect(cloud="gx")
        self.log = Logger(name='inspector_logger', log_file='logfile.log')
        self.logger_instance = self.log.getLogger()
        #self.logger_instance = self.log.logger # basically the same

    def exampleLog(self):
        self.logger_instance.info('Logging from AnotherClass')
        self.logger_instance.debug('Debug message from AnotherClass')


    def load_env_from_yaml(self):
        with open(self.env_file_path, 'r') as file:
            env = yaml.safe_load(file)
        #    self.logger_instance.debug("success:found environment variables")
        return env

    def check_network_existence(self, network_name):
        try:
            networks = self.client.network.networks()
            for net in networks:
                if net["name"] == network_name:
                    #self.logger.info(f"Network found: {network_name}")
                    return True
                else: continue
            #TODO: log all of the networks to logfile
        except Exception as e:
            #self.logger.error(f"Error while checking network existence: {e}")
            print(f"Error while checking network existence: {e}")

# Example usage:
if __name__ == "__main__":

    inspector = Inspector()
    inspector.exampleLog()
    if inspector.check_network_existence("ext01"):
        print("Network exists!")
    else:
        print("Network does not exist.")


# new_rootlogger = Logger()
# logger_instance = new_rootlogger.getLogger()
# logger_instance.info('This is an info message')
# logger_instance.debug('This is a debug message')
