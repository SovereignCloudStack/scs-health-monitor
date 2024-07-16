from behave import given, when, then
from kubernetes import client, config
import requests
import time


class KubernetesTestSteps:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.response = None
        self.ping_response = None

    @given('a Kubernetes cluster')
    def step_given_kubernetes_cluster(self, context):
        # Ensure we can connect to the cluster
        self.v1.list_node()

    @when('I create a container named "{container_name}"')
    def step_when_create_container(self, context, container_name):
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
        self.v1.create_namespaced_pod(namespace="default", body=pod)
        time.sleep(10)  # Wait for the pod to be created

    @then('the container "{container_name}" should be running')
    def step_then_container_running(self, context, container_name):
        pod = self.v1.read_namespaced_pod(name=container_name, namespace="default")
        assert pod.status.phase == "Running"

    @when('I send an HTTP request to "{container_name}"')
    def step_when_send_http_request(self, context, container_name):
        pod = self.v1.read_namespaced_pod(name=container_name, namespace="default")
        ip = pod.status.pod_ip
        self.response = requests.get(f"http://{ip}")

    @then('the response status code should be 200')
    def step_then_response_status_code(self, context):
        assert self.response.status_code == 200

    @when('"{src_container}" pings "{dst_container}"')
    def step_when_ping(self, context, src_container, dst_container):
        src_pod = self.v1.read_namespaced_pod(name=src_container, namespace="default")
        dst_pod = self.v1.read_namespaced_pod(name=dst_container, namespace="default")
        ip = dst_pod.status.pod_ip

        exec_command = [
            '/bin/sh',
            '-c',
            f'ping -c 1 {ip}'
        ]
        response = self.v1.connect_get_namespaced_pod_exec(
            name=src_container,
            namespace="default",
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False
        )
        self.ping_response = response

    @then('the ping should be successful')
    def step_then_ping_successful(self, context):
        assert "1 packets transmitted, 1 received" in self.ping_response


k8s_steps = KubernetesTestSteps()


@given('a Kubernetes cluster')
def step_given_kubernetes_cluster(context):
    k8s_steps.step_given_kubernetes_cluster(context)


@when('I create a container named "{container_name}"')
def step_when_create_container(context, container_name):
    k8s_steps.step_when_create_container(context, container_name)


@then('the container "{container_name}" should be running')
def step_then_container_running(context, container_name):
    k8s_steps.step_then_container_running(context, container_name)


@when('I send an HTTP request to "{container_name}"')
def step_when_send_http_request(context, container_name):
    k8s_steps.step_when_send_http_request(context, container_name)


@then('the response status code should be 200')
def step_then_response_status_code(context):
    k8s_steps.step_then_response_status_code(context)


@when('"{src_container}" pings "{dst_container}"')
def step_when_ping(context, src_container, dst_container):
    k8s_steps.step_when_ping(context, src_container, dst_container)


@then('the ping should be successful')
def step_then_ping_successful(context):
    k8s_steps.step_then_ping_successful(context)