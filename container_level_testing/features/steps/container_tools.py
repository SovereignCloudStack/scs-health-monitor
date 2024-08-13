from pprint import pprint

from kubernetes import client, config


def check_if_container_running(client, container_name, namespace):
    pod = client.read_namespaced_pod(name=container_name, namespace=namespace)
    assert pod.status.phase == "Running"


def create_container(container_name):
    return client.V1Pod(
        metadata=client.V1ObjectMeta(name=container_name, labels={"app": f"{container_name}"}),
        spec=client.V1PodSpec(
            containers=[client.V1Container(
                name=container_name,
                image="busybox",
                command=["sleep", "3600"],
                ports=[client.V1ContainerPort(container_port=80)]
            )]
        )
    )


def create_service(service_name, port):
    return client.V1Service(
        metadata=client.V1ObjectMeta(name=service_name),
        spec=client.V1ServiceSpec(
            selector={"app": service_name},
            ports=[client.V1ServicePort(
                protocol="TCP",
                target_port=int(port),
                port=int(port)
            )], type="NodePort"
        )
    )


def get_node_port(service_name, namespace):
    # Load kubeconfig and initialize the API client
    config.load_kube_config()
    v1 = client.CoreV1Api()

    try:
        # Get the service details
        service = v1.read_namespaced_service(name=service_name, namespace=namespace)
        for port in service.spec.ports:
            if port.node_port:
                return port.node_port
        raise Exception(f"No node port found for service {service_name}")
    except client.exceptions.ApiException as e:
        pprint(f"Exception when calling CoreV1Api->read_namespaced_service: {e}")
        raise
