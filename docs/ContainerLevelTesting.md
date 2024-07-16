# Container level testing documentation

TODO: description

## Environment configuration
### MacOS:

```commandline
brew install minikube
brew install kind
```

### Linux
```commandline
apt-get install minikube
apt-get install kind
```


Create and place kubeconfig file in i.e. "~/.kube/config" using example below:

```yaml
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <base64-encoded-ca-cert>
    server: https://127.0.0.1:8443
  name: local
contexts:
- context:
    cluster: local
    user: local-user
  name: local-context
current-context: local-context
kind: Config
preferences: {}
users:
- name: local-user
  user:
    client-certificate-data: <base64-encoded-client-cert>
    client-key-data: <base64-encoded-client-key>
```



