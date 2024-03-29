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


class Recover:
    def __init__(self, cloud='gx'):
        self.conn = self._connect(cloud)

    def _connect(self, cloud):
        return openstack.connection.from_config(cloud_name=cloud)

    def delete_networks(self):
        try:
            for network in self.conn.network.networks():
                for port in self.conn.network.ports(network_id=network.id):
                    self.conn.network.delete_port(port.id)
                    print(f"Port {port.id} deleted.")

                self.conn.network.delete_network(network.id)
                print(f"Network with ID {network.id} has been deleted.")
        except Exception as e:
            print(f"network {network.name} can't be deleted because exception {e} is raised.")

    def delete_subnets(self):
        try:
            for subnet in self.conn.network.subnets():
                self.delete_subent_ports(subnet=subnet)
                self.conn.network.delete_subnet(subnet.id)
                print(f"Subnet with ID {subnet.id} has been deleted.")
        except Exception as e:
            print(f"subnet {subnet.name} can't be deleted because exception {e} is raised.")

    def delete_security_groups(self):
        try:
            for group in self.conn.network.security_groups():
                self.conn.network.delete_security_group(group.id)
                print(f"Security group with ID {group.id} has been deleted.")
        except Exception as e:
            print(f"security group {group.name} can't be deleted because exception {e} is raised.")


    def delete_security_group_rules(self):
        try:
            for rule in self.conn.network.security_group_rules():
                self.conn.network.delete_security_group_rule(rule.id)
                print(f"Security group rule with ID {rule.id} has been deleted.")
        except Exception as e:
            print(f"security group rule {rule.name} can't be deleted because exception {e} is raised.")

    def delete_routers(self):
        try:
            for router in self.conn.network.routers():
                self.delete_ports_router(router=router)
                self.conn.network.delete_router(router.id)
                print(f"Router with ID {router.id} has been deleted.")
        except Exception as e:
            print(f"router {router.name} can't be deleted because exception {e} is raised.")

    def get_jumphosts(self):
        jumphosts = []
        for server in self.conn.compute.servers():
            if 'jumphost' in server.name.lower():
                jumphosts.append(server)
        return jumphosts

    def delete_jumphosts(self):
        for jumphost in self.get_jumphosts():
            self.conn.compute.delete_server(jumphost.id)

    def delete_ports_router(self, router):
        for port in self.conn.network.ports(device_id=router.id):
            self.conn.network.remove_interface_from_router(router.id, port_id=port.id)
            print(f"Port {port.id} detached from router {router.id}")

    def delete_subent_ports(self, subnet):
        for port in self.conn.network.ports(network_id=subnet.id):
            for fixed_ip in port.fixed_ips:
                if fixed_ip['subnet_id'] == subnet.id:
                    self.conn.network.delete_port(port.id)
                    print(f"Port {port.id} deleted.")


if __name__ == "__main__":
    recover = Recover()
    recover.delete_security_group_rules()
    recover.delete_security_groups()
    recover.delete_routers()
    recover.delete_subnets()
    recover.delete_networks()

# if __name__ == "__main
#     inspector = Inspector()
#     if inspector.check_network_existence("ext01"):
#         print("Network exists!")
#     else:
#         print("Network does not exist.")
