from pprint import pprint


class ContainerCollector:
    def __init__(self):
        self.containers = list()
        self.services = list()
        self.persistent_volume = list()
        self.persistent_volume_claim = list()


def get_node_port(client, service_name, namespace):
    try:
        # Get the service details
        service = client.read_namespaced_service(name=service_name, namespace=namespace)
        for port in service.spec.ports:
            if port.node_port:
                return port.node_port
        raise Exception(f"No node port found for service {service_name}")
    except client.exceptions.ApiException as e:
        pprint(f"Exception when calling CoreV1Api->read_namespaced_service: {e}")
        raise
