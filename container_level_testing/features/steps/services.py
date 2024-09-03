from kubernetes import client


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
