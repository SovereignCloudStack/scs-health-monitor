from kubernetes import client

def check_if_pod_running(client, container_name, namespace):
    pod = client.read_namespaced_pod(name=container_name, namespace=namespace)
    return pod.status.phase == "Running"


def generate_pod_object(pod_name):
    return client.V1Pod(
        metadata=client.V1ObjectMeta(name=pod_name, labels={"app": f"{pod_name}"}),
        spec=client.V1PodSpec(
            containers=[client.V1Container(
                name=pod_name,
                image="docker.io/library/alpine:3.20.2",
                command=["sh", "-c", "apk add --no-cache tini-static && /sbin/tini-static -p SIGKILL -g -v sleep infinity"],
                ports=[client.V1ContainerPort(container_port=80)]
            )]
        )
    )
