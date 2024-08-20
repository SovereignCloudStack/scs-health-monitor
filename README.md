# SCS Health Monitor

Welcome to the SCS Health Monitor project! This repository is dedicated to setting up scenarios for functionality and load testing on a deployed OpenStack environment. We utilize Gherkin language to write testing scenarios, and Python's Behave library to execute these tests.

## Description

The SCS Health Monitor project aims to ensure the robustness and reliability of OpenStack environments by simulating various scenarios and assessing their performance under different loads. By employing Gherkin language and Behave library, we can define clear, human-readable test cases that cover a wide range of functionalities, from basic system checks to complex stress tests.

## Getting Started

To get started with the SCS Health Monitor project, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies listed in the `requirements.txt` file.
3. Review the existing Gherkin scenarios in the `features` directory to understand the testing coverage.
4. Create a *clouds.yaml* file int the root of the repository to be able to perform API calls to OpenStack.
5. Create a *env.yaml* file containing configuration needed for performing the tests
6. Execute the tests using Behave library to validate the functionality and performance of your OpenStack environment.

## Usage

Here are some basic commands to run the tests:

```bash
behave             # Run all scenarios
behave features/   # Run scenarios in a specific feature file
behave -t @tag     # Run scenarios with a specific tag

# EXAMPLES

# Runs openstack_create_network.feature feature
behave ./features/openstack_create_network.feature

#runs both features
behave

# Runs tests tagged with "network" tag
behave --tags=network
```

There is a possibility to run it on the [behavex](https://github.com/hrcorval/behavex) framework as well. To get more information, [here](https://pypi.org/project/behavex/) is a link to the documentation.
Here are some basic commands to run the tests:

```bash
behavex                            # Run all scenarios parallel - not recomended 
behavex --parallel-scheme feature  # Run all of the scenarios, but parallel only the features
behavex features/                  # Run scenarios in a specific feature file
behavex -t @tag                    # Run scenarios with a specific tag

# EXAMPLES

# Runs openstack_create_network.feature feature
behavex ./features/openstack_create_network.feature

# Runs tests tagged with "cleanup" tag
behavex --tags=cleanup
```

## Setting up Prometheus and Prometheus Push Gateway locally
For the purposes of gathering information from the test cases being performed against OpenStack, Prometheus metrics are being gathered during excecution of the test, then later these metrics are pushed to a Prometheus Push Gateway.

[Here](./docs/ObservabilityStack/SetupObservabilityStack.md) you can find a useful quickstart quide on setting up Promethus Stack and Prometheus push gateway locally.

## Exporting metrics to Prometheus Push Gateway
To be able to push the metrics gathered during test executions, you must first configure the prometheus push gateway endpoint. You achieve this by adding these lines to a *env.yaml*:

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

## Collaborators
- Piotr Bigos [@piobig2871](https://github.com/piobig2871)
- Erik Kostelanský [@Erik-Kostelansky-dNation](https://github.com/Erik-Kostelansky-dNation)
- Katharina Trentau [@fraugabel](https://github.com/fraugabel)
- Ľubomír Dobrovodský [@dobrovodskydnation](https://github.com/dobrovodskydnation)
- Tomáš Smädo [@tsmado](https://github.com/tsmado)

## Useful links

### [Openstack python SDK documentation](https://docs.openstack.org/openstacksdk/latest/user/)
### [Openstack CLI tool documentation](https://docs.openstack.org/python-openstackclient/latest/)
### [Parameterisation of tests using scenario outlines](https://jenisys.github.io/behave.example/tutorials/tutorial04.html)
### [Short but concise tutorial on how to setup behave test scenarios](https://behave.readthedocs.io/en/stable/tutorial.html)


