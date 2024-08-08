from behave import given, when, then
from kubernetes import client, config
import requests
import time
import subprocess
from http import HTTPStatus
import container_level_testing.features.steps.container_tools as tools


class KubernetesTestSteps:

    @given('a Kubernetes cluster')
    def kubernetes_cluster(context):
        config.load_kube_config()
        context.v1 = client.CoreV1Api()
        context.response = None
        context.ping_response = None
        context.v1.list_node()
        result = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to connect to Kubernetes cluster: {result.stderr}")

    @when('I create a container named {container_name}')
    def create_container(context, container_name):
        pod = tools.create_container(container_name=container_name)
        context.v1.create_namespaced_pod(namespace="default", body=pod)
        time.sleep(10)

    @then('the container {container_name} should be running')
    def container_running(context, container_name):
        tools.check_if_container_running(context.v1, container_name=container_name)

    @when('I create a service for the container named {container_name} on {port}')
    def create_service(context, container_name, port):
        service_manifest = f"""
    apiVersion: v1
    kind: Service
    metadata:
      name: {container_name}
    spec:
      selector:
        app: {container_name}
      ports:
        - protocol: TCP
          port: {port}
          targetPort: {port}
          nodePort: 30007
    """
        result = subprocess.run(
            ["kubectl", "apply", "-f", "-"], input=service_manifest, capture_output=True,
            text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to create service: {result.stderr}")
        time.sleep(15)

    @then('the service for {container_name} should be running')
    def service_running(context, container_name):
        result = subprocess.run(["kubectl", "get", "service", container_name], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to get service status: {result.stderr}")
        status = result.stdout
        assert container_name in status, f"Expected service {container_name} to be running"

    # @when('I send an HTTP request to {container_name}')
    # def send_http_request(context, container_name):
    #     result = subprocess.run(
    #         ["kubectl", "get", "service", container_name, "-o", "jsonpath='{.spec.clusterIP}'"],
    #         capture_output=True, text=True)
    #     if result.returncode != 0:
    #         raise Exception(f"Failed to get service IP: {result.stderr}")
    #     ip = result.stdout.strip().strip("'")
    #     context.response = requests.get(f"http://{ip}")

    @when('I send an HTTP request to {container_name} from outside the cluster using node IP node_ip')
    def send_http_request(context, container_name):
        node_ip = subprocess.run(
            ["kubectl", "get", "service", container_name, "-o", "jsonpath='{.spec.clusterIP}'"],
            capture_output=True, text=True)
        ip = node_ip.stdout.strip().strip("'")
        node_port = tools.get_node_port(container_name)  # Get the node port dynamically
        try:
            context.response = requests.get(f"http://{ip}:{node_port}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to send HTTP request: {e}")

    @given('a container running a web server named {container_name}')
    def container_running_web_server(context, container_name):
        context.create_container(context, container_name)
        context.container_running(context, container_name)

    @then('the response status code should be 200')
    def response_status_code(context):
        assert context.response.status_code == HTTPStatus.OK

    @when('{src_container} pings {dst_container}')
    def ping(context, src_container, dst_container):
        result = subprocess.run(["kubectl", "exec", src_container, "--", "ping", "-c", "1", dst_container],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Ping failed: {result.stderr}")
        context.ping_response = result.stdout

    @then('the ping should be successful')
    def ping_successful(context):
        assert "1 packets transmitted, 1 received" in context.ping_response

    @when('I delete the container named {container_name}')
    def delete_container(context, container_name):
        context.v1.delete_namespaced_pod(name=container_name, namespace="default", body=client.V1DeleteOptions())
        # context.logger(f"Wait for the pod to be deleted")
        time.sleep(10)

    @then('the container {container_name} should be deleted')
    def container_deleted(context, container_name):
        try:
            context.v1.read_namespaced_pod(name=container_name, namespace="default")
            raise AssertionError("Pod still exists")
        except client.exceptions.ApiException as e:
            if e.status == 404:
                pass
                # context.logger(f"Pod is successfully deleted")
            else:
                raise e
