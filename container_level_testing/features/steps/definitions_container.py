from behave import given, when, then
from kubernetes import client, config
import requests
import time
from http import HTTPStatus

##TODO: pass the kubeconfig


class KubernetesTestSteps:

    @given('a Kubernetes cluster')
    def step_given_kubernetes_cluster(context):
        config.load_kube_config()
        context.v1 = client.CoreV1Api()
        context.response = None
        context.ping_response = None
        context.v1.list_node()

    @when('I create a container named {container_name}')
    def step_when_create_container(context, container_name):
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(name=container_name),
            spec=client.V1PodSpec(
                containers=[client.V1Container(
                    name=container_name,
                    image="nginx",
                    ports=[client.V1ContainerPort(container_port=80)]
                )]
            )
        )
        context.v1.create_namespaced_pod(namespace="default", body=pod)
        time.sleep(10)

    @then('the container {container_name} should be running')
    def step_then_container_running(context, container_name):
        pod = context.v1.read_namespaced_pod(name=container_name, namespace="default")
        assert pod.status.phase == "Running"

    @when('I send an HTTP request to {container_name}')
    def step_when_send_http_request(context, container_name):
        pod = context.v1.read_namespaced_pod(name=container_name, namespace="default")
        ip = pod.status.pod_ip
        context.response = requests.get(f"http://{ip}")

    @given('a container running a web server named {container_name}')
    def step_given_container_running_web_server(context, container_name):
        context.step_when_create_container(context, container_name)
        context.step_then_container_running(context, container_name)

    @then('the response status code should be 200')
    def step_then_response_status_code(context):
        assert context.response.status_code == HTTPStatus.OK

    @when('{src_container} pings {dst_container}')
    def step_when_ping(context, src_container, dst_container):
        src_pod = context.v1.read_namespaced_pod(name=src_container, namespace="default")
        dst_pod = context.v1.read_namespaced_pod(name=dst_container, namespace="default")
        ip = dst_pod.status.pod_ip

        exec_command = [
            '/bin/sh',
            '-c',
            f'ping -c 1 {ip}'
        ]
        response = context.v1.connect_get_namespaced_pod_exec(
            name=src_container,
            namespace="default",
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False
        )
        context.ping_response = response

    @then('the ping should be successful')
    def step_then_ping_successful(context):
        assert "1 packets transmitted, 1 received" in context.ping_response

    @when('I delete the container named {container_name}')
    def step_when_delete_container(context, container_name):
        context.v1.delete_namespaced_pod(name=container_name, namespace="default", body=client.V1DeleteOptions())
        # context.logger(f"Wait for the pod to be deleted")
        time.sleep(10)

    @then('the container {container_name} should be deleted')
    def step_then_container_deleted(context, container_name):
        try:
            context.v1.read_namespaced_pod(name=container_name, namespace="default")
            raise AssertionError("Pod still exists")
        except client.exceptions.ApiException as e:
            if e.status == 404:
                pass
                # context.logger(f"Pod is successfully deleted")
            else:
                raise e