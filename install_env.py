import subprocess
from pprint import pprint


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {result.stderr}")
    pprint(result.stdout)


def install_ingress_controller():
    """
    Environment preparation
    :return: Installation of Nginx Ingress, Nginx Ingress Controller
    """
    run_command("helm repo update")
    run_command("helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx")
    run_command(
        "helm install nginx-ingress ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace")
    run_command("kubectl get svc -n ingress-nginx")

if __name__ == __name__:
    install_ingress_controller()