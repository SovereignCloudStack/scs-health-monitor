# Kubernetes BDD Testing Framework Documentation
## Overview

This framework is designed to facilitate Behavior-Driven Development (BDD) for testing Kubernetes deployments using the
behave Python library. The framework allows you to write human-readable tests that validate Kubernetes clusters, pods,
services, and other resources.

Before you begin, ensure you have the following installed on your machine:

Python 3.8+
pip (Python package installer)
kubectl (Kubernetes command-line tool)
Helm (Kubernetes package manager)




## Usage

1. Clone the Repository:
``` bash
git clone https://github.com/SovereignCloudStack/scs-health-monitor
cd scs-health-monitor
```
2. Set Up a Virtual Environment:

It's recommended to use a virtual environment to avoid conflicts with other Python packages.


``` bash
# create python virtual environment
python3 -m venv <environment_name>

# activate the python virtual environment in windows command prompt
<environment_name>/Scripts/activate   

# activate the python virtual environment in Unix or MacOS
source <environment_name>/bin/activate

# install all the python dependencies
python -m pip install -r requirements.txt 
```


3. Install Required Python Packages:

Install all necessary Python packages using pip.

```bash
pip install -r requirements.txt
```

4. Install Additional Tools (Optional) or run script install_env.py:

If you need to install and manage an NGINX Ingress controller, you'll need helm.

For MacOS:
```bash
brew install helm
```

For Linux:
```bash 
sudo apt-get install helm
```

For Windows:

The easeiest way is to use linux kernel for windows and proceed there.

____

In this repository (under main directory) you have to create two files that will be referenced by `env.yaml` and `clouds.yaml`
* env.yaml:
```
   OS_AUTH_TYPE: ""
   OS_AUTH_URL: ""
   OS_IDENTITY_API_VERSION: ""
   OS_REGION_NAME: ""
   OS_INTERFACE: ""
   OS_APPLICATION_CREDENTIAL_ID: ""
   OS_APPLICATION_CREDENTIAL_SECRET: ""
   OS_PROJECT_NAME: ""
   OS_USER_DOMAIN_NAME: ""
   OS_PROJECT_DOMAIN_NAME: "" 

   ```
* clouds.yaml:
```
clouds:
  gx:
    region_name:
    auth_type:
    auth_url:
    identity_api_version:
    interface:
    application_credential_id:
    application_credential_secret:
```


## Configuration
### Kubernetes Configuration

Ensure that your Kubernetes configuration file (kubeconfig) is correctly set up. This file is typically located at ~/.kube/config. The framework uses this configuration to interact with your Kubernetes cluster.

If you want to use a specific context from your kubeconfig, you can set it using:
```bash
kubectl config use-context scs-vp12
```

### Helm Configuration

For Ingress management, you need to add the NGINX Ingress repository and install the Ingress controller.

```bash
helm install nginx-ingress ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace
```

### Running Tests
Writing Test Scenarios

Tests are written in .feature files using Gherkin syntax. Each scenario represents a feature of the application you want to test.

Example feature file (container_creation.feature):

```gherkin

Feature: Container Management

  Scenario: Creating a simple container
    Given a Kubernetes cluster
    When I create a container named test-container
    Then the container test-container should be running

  Scenario: Creating a service for the container
    Given a container running a web server named web-container
    When I create a service for the container named web-container on 80
    Then the service for web-container should be running
    When I send an HTTP request to web-container
    Then the response status code should be 200
```

### Running the Tests

You can run the tests using the behave command from the root of your project:

```bash
behave
```

This will execute all the scenarios defined in the .feature files within the features directory.

### Example Command to Run a Specific Feature File

To run a specific feature file, use:
```bash
behave container_level_testing/features/container_creation.feature
```

### Adding New Features
Creating New Step Definitions

To add new behavior or extend existing features, define new steps in the Python files located in container_level_testing/features/steps/. These files map Gherkin steps to Python code.

```python
@given('describe what test is doing')
def name_of_the_test(context):
    ## Body of the test  
```

### Creating New Feature Files

1. Create a New Feature File:

Add a new .feature file in the features directory.

2. Write Scenarios in Gherkin Syntax:

Define the behavior you want to test using Given-When-Then steps.
```gherkin
Feature: New Kubernetes Feature

  Scenario: A new feature scenario
    Given name of the function 
    When name of another function with logic
    Then step with assertion to verify if step before was succeded 
```

3. Implement the Step Definitions:

Add the corresponding step definitions in the appropriate .py file under features/steps/.

#### Modifying Existing Features

1. Update the Feature File:

Modify the .feature file to reflect the new behavior or changes.

2. Update the Step Definitions:

Modify the corresponding step definitions in the .py file.

#### Setting Up Ingress

To add ingress resources:

Create Ingress YAML:

Create an ingress resource file my-ingress.yaml with the desired settings.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: my-project.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80

```

2. Apply the Ingress Resource:

Use the following command to apply the ingress resource:
```bash
kubectl apply -f my-ingress.yaml
```

## Troubleshooting

### Common Errors

* Connection Errors: Ensure that Kubernetes and Ingress services are correctly configured and running.

* Port Conflicts: Ensure that the specified ports are not already in use. Modify the nodePort or use dynamic assignment.

* Timeouts: Adjust the timeout settings in the test code if the service or container takes longer to initialize.

#### Debugging Tips
* Check Pod Logs:
```bash
kubectl logs <pod-name>
```
* Check Service and Pod Status:
```bash
kubectl get services
kubectl get pods
```

## Observability stack

For informations about setting up Observability Stack, please use this [file](https://github.com/SovereignCloudStack/scs-health-monitor/blob/main/docs/ObservabilityStack/SetupObservabilityStack.md)

___

## Adding fixes/new functionalities to the project flow:

1) Create branch for issue `git checkout -b SPACECAT-<issue_number>-<issue_name>`.
2) Add the changes made `git add -u` or `git add <file_name>`.
3) Commit the changes using `git commit -s -m "message"`.
   - The "-s" flag is important, the commit won't go through otherwise
4) To push the current branch and the changes and set the remote as upstream, use `git push --set-upstream origin SPACECAT-<issue_number>-<issue_name>`.
   - Alternatively push the changes if the branch already exists in the remote repository.
5) After work is done, create a pull request for the branch.
6) Ask another team member to review the changes, when he approves the changes, merge the chages into main branch.

___

## Conclusion

This framework provides a robust, BDD-based approach to testing Kubernetes clusters and resources. By following the above instructions, you can extend, modify, and run tests tailored to your specific needs.

Feel free to customize the framework to accommodate new Kubernetes features and application requirements.