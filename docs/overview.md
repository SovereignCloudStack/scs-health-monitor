# SCS Health Monitor

Welcome to the SCS Health Monitor project! This repository is dedicated to setting up scenarios for functionality and load testing on a deployed OpenStack environment. We utilize Gherkin language to write testing scenarios, and Python's Behave library to execute these tests.

## Description

The SCS Health Monitor project aims to ensure the robustness and reliability of OpenStack environments by simulating various scenarios and assessing their performance under different loads. By employing Gherkin language and Behave library, we can define clear, human-readable test cases that cover a wide range of functionalities, from basic system checks to complex stress tests.

## Getting Started

To get started with the SCS Health Monitor project, follow these steps:

1. Clone [healt-monitor repository](https://github.com/SovereignCloudStack/scs-health-monitor) to your local machine.
   ```
   git clone git@github.com:SovereignCloudStack/scs-health-monitor.git
   cd scs-health-monitor
   ```
2. Install the required dependencies
    * listed in the `[Dockerfile](https://github.com/SovereignCloudStack/scs-health-monitor/blob/main/Dockerfile)` file
      (see: `apt-get ...`)
    * listed in the `[requirements.txt](https://github.com/SovereignCloudStack/scs-health-monitor/blob/main/requirements.txt)` file by executing the following command:
      ```
      ./scs-health-monitor deps
      ```
3. Review the existing Gherkin scenarios in the `[cloud_level_testing/features](https://github.com/SovereignCloudStack/scs-health-monitor/tree/main/cloud_level_testing/features)` and `[container_level_testing/features](https://github.com/SovereignCloudStack/scs-health-monitor/tree/main/container_level_testing/features)` directories to understand the testing coverage.
4. Create a openstack project with a user with "manager" privileges
5. Create a `clouds.yaml` ([example](/assets/config-examples/clouds.yaml)) file in the root of the repository-clone to configure API access to OpenStack.
6. Create a `env.yaml` ([example](/assets/config-examples/env.yaml)) file containing configuration needed for performing the tests.
   (Configure at least the `CLOUD_NAME` to specify which project should be used)
7. Execute the tests using Behave library to validate the functionality and performance of your OpenStack environment.
   (see [next section](#using-the-test-framework))

## Using the test framework

### Execute a specific test

```bash
./scs-health-monitor behave cloud_level_testing/features/openstack_create_network.feature
```

Here are some basic commands to run the tests:

### Execute a series of tests

*  Run all scenarios for IaaS
   ```bash
   ./scs-health-monitor behave cloud_level_testing/features/
   ```
*  Run all scenarios for KaaS
   ```bash
   ./scs-health-monitor behave container_level_testing/features/
   ```
*  Run all scenarios for IaaS with the "network" and the "cleanup" tag
   ```bash
   ./scs-health-monitor behave --tags=network  cloud_level_testing/features/
   ./scs-health-monitor behave --tags=cleanup  cloud_level_testing/features/
   ```

* Run all of the IaaS scenarios, but parallel only the features
   ```bash
   ./scs-health-monitor behavex --parallel-scheme cloud_level_testing/features/
   ```

There is a possibility to run it on the [behavex](https://github.com/hrcorval/behavex) framework as well. To get more information, [here](https://pypi.org/project/behavex/) is a link to the documentation.
Here are some basic commands to run the tests:

## Publish results to Prometheus

The scs-health-monitor is capable to puhlish the results to a prometheus instance.
Details of the available measurements are available in the [METRIC OVERVIEW](docs/Metric_List.md).

### Setting up Prometheus and Prometheus Push Gateway locally

For the purposes of gathering information from the test cases being performed against OpenStack, Prometheus metrics are being gathered during excecution of the test, then later these metrics are pushed to a Prometheus Push Gateway.

[Here](./docs/ObservabilityStack/SetupObservabilityStack.md) you can find a useful quickstart quide on setting up Promethus Stack and Prometheus push gateway locally.

### Exporting metrics to Prometheus Push Gateway

To be able to push the metrics gathered during test executions, you must first configure the prometheus push gateway endpoint. You achieve this by adding these lines to a *[env.yaml](/assets/config-examples/env.yaml)*:

``` bash
# Required
# If not present the metrics won't
# be pushed by the test scenarios
PROMETHEUS_ENDPOINT: "localhost:30001"

# Optional (default: "SCS-Health-Monitor")
# Specify the job label value that
# gets added to the metrics
PROMETHEUS_BATCH_NAME: "SCS-Health-Monitor"

# Required
# The name of the cloud from clouds.yaml
# that the test scenarios will be ran on
CLOUD_NAME: "gx"

# Optional (default: true)
# Apply start time and stop time to prometheus batch name
APPEND_TIMESTAMP_TO_BATCH_NAME: true
```

This *env.yaml* file must be placed in the root of the repository. This is where you should be also issuing all the *behave <...>* commands to execute the test scenarios.

## Use a docker image

* Create a docker image
  ```bash
  docker build --progress plain -t scs-health-monitor -f Dockerfile .
  ```
* Execute a docker image
  ```bash
  sudo chown 1001:1001 ./env.yaml ./clouds.yaml ./ca-certificates.crt
  DOCKER_MOUNTS="-v ./env.yaml:/installation/env.yaml -v ./clouds.yaml:/installation/clouds.yaml -v ./ca-certificates.crt:/installation/ca-certificates.crt"
  # A shell
  docker run -ti ${DOCKER_MOUNTS?not set} --rm --entrypoint /bin/bash --name scs-health-monitor scs-health-monitor
  # Entrypoint execution
  docker run -ti ${DOCKER_MOUNTS?not set} --rm --name scs-health-monitor scs-health-monitor behave <ARGUMENTS>
  docker run -ti ${DOCKER_MOUNTS?not set} --rm --name scs-health-monitor scs-health-monitor behave cloud_level_testing/features/openstack_create_network.feature
  ```

## Collaborators

- Piotr Bigos [@piobig2871](https://github.com/piobig2871)
- Erik Kostelanský [@Erik-Kostelansky-dNation](https://github.com/Erik-Kostelansky-dNation)
- Katharina Trentau [@fraugabel](https://github.com/fraugabel)
- Ľubomír Dobrovodský [@dobrovodskydnation](https://github.com/dobrovodskydnation)
- Tomáš Smädo [@tsmado](https://github.com/tsmado)

## Useful links and references

* [Openstack python SDK documentation](https://docs.openstack.org/openstacksdk/latest/user/)
* [Openstack CLI tool documentation](https://docs.openstack.org/python-openstackclient/latest/)
* [Parameterisation of tests using scenario outlines](https://jenisys.github.io/behave.example/tutorials/tutorial04.html)
* [Short but concise tutorial on how to setup behave test scenarios](https://behave.readthedocs.io/en/stable/tutorial.html)
* [The legacy but complete implementation](https://github.com/SovereignCloudStack/openstack-health-monitor)
