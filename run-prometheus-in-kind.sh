#!bash

set -e

SCRIPT_DIR=$(dirname $(readlink -f "$0"))
KUBECONFIG_PATH="$SCRIPT_DIR/kubeconfig_kind_scs-hm-prometheus"
KIND_CLUSTER_CONFIG="$SCRIPT_DIR/docs/ObservabilityStack/kind/kind-config-prometheus.yaml"

if kind get clusters | grep scs-hm-prometheus; then
  echo "KinD cluster scs-hm-prometheus already exists, skipping creation"
else
  # create KinD cluster with a config that maps the NodePort ports on the host machine
  kind create cluster --config "$KIND_CLUSTER_CONFIG" --kubeconfig "$KUBECONFIG_PATH" --name "scs-hm-prometheus"
fi

if [[ ! -f "$KUBECONFIG_PATH" ]]; then
  echo "$KUBECONFIG_PATH is not a file, aborting"
  exit
fi

export KUBECONFIG="$KUBECONFIG_PATH"

kubectl cluster-info --context kind-scs-hm-prometheus --kubeconfig "$KUBECONFIG_PATH"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# default prometheus login: admin/prom-operator
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack --version 57.0.3 -f "$SCRIPT_DIR/docs/ObservabilityStack/Values/PrometheusStackValues.yaml"
helm install prometheus-pushgateway prometheus-community/prometheus-pushgateway --version 2.8.0 -f "$SCRIPT_DIR/docs/ObservabilityStack/Values/PrometheusPushGateway.yaml"

kubectl apply -f "$SCRIPT_DIR/docs/ObservabilityStack/k8s/nodePorts.yaml"

#kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090
#kubectl port-forward svc/prometheus-pushgateway 9091:9091
