from kubernetes import client


def check_if_container_running(client, container_name):
    pod = client.read_namespaced_pod(name=container_name, namespace="default")
    assert pod.status.phase == "Running"


def create_conainer(container_name):
    client.V1Pod(
        metadata=client.V1ObjectMeta(name=container_name),
        spec=client.V1PodSpec(
            containers=[client.V1Container(
                name=container_name,
                image="nginx",
                ports=[client.V1ContainerPort(container_port=80)]
            )]
        )
    )
