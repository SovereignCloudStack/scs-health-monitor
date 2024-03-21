# Setup observability stack

## Prerequisites
Kubernetes is required to setup this observability stack consisting of Prometheus, Grafana and Prometheus push gateway.
One recommendation for setting up a local Kubernetes environment is to use [KIND (Kubernetes in Docker)](https://kind.sigs.k8s.io/). KIND provides a lightweight way to create Kubernetes clusters using Docker containers. [Docker Desktop](https://docs.docker.com/desktop/kubernetes/) also has support for kubernetes.

## Setup process
To set up Prometheus stack and Prometheus Pushgateway on local Kubernetes using Helm, you can follow these steps:

1) Add Helm Chart Repositories:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 
helm repo update
```

2) Install Prometheus Stack:

```bash
helm install my-kube-prometheus-stack prometheus-community/kube-prometheus-stack --version 57.0.3 -f "./Values/PrometheusStackValues.yaml"
```

This command will install the Prometheus stack on your Kubernetes cluster [using these values](./Values/PrometheusStackValues.yaml).

3) Install Prometheus Pushgateway:

```bash
helm install my-prometheus-pushgateway prometheus-community/prometheus-pushgateway --version 2.8.0 -f "./Values/PrometheusPushGateway.yaml"
```

This command will install Prometheus Pushgateway on your Kubernetes cluster [using these values](./Values/PrometheusPushGateway.yaml).

4) Set Docker Context:

```bash
kubectl config get-contexts
kubectl config use-context docker-desktop
```

Ensure that the Docker context is correctly set to your local Kubernetes cluster.

5) Expose Services Locally:

```bash
kubectl apply -f ./k8s/nodePorts.yaml
```

This command will apply the configuration to expose services using nodePort service on Kubernetes.

An alternative to using NodePort for exposing services to localhost in a local Kubernetes setup is to use kubectl port-forward. This command allows you to forward local ports to a port on a specific pod within the Kubernetes cluster. Here's how you can use it:

6) Port Forwarding for Prometheus Stack:

```bash

kubectl port-forward svc/<prometheus-service-name> <local-port>:<prometheus-port>
```

Replace \<prometheus-service-name\> with the actual name of the Prometheus service in your Kubernetes cluster. \<local-port\> is the port number on your localhost where you want to access Prometheus, and \<prometheus-port\> is the port on which Prometheus is running within the cluster. The same applies to prometheus push gateway or any other service you may want to expose.

For example:

```bash
kubectl port-forward svc/my-kube-prometheus-stack-prometheus 9090:9090
kubectl port-forward svc/my-prometheus-pushgateway 9091:9091
```

Make sure to replace "./Values/PrometheusStackValues" with the actual path to your Prometheus Stack values file. Also, adjust the path to the nodePorts.yaml file if it's located in a different directory.

Remember to replace placeholders such as my-kube-prometheus-stack and my-prometheus-pushgateway with appropriate names for your deployments.

Once you've executed these commands, Prometheus stack and Prometheus Pushgateway should be set up and accessible on your local Kubernetes cluster.