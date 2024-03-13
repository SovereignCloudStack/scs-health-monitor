# SCS Health Monitor

Welcome to the SCS Health Monitor project! This repository is dedicated to setting up scenarios for functionality and load testing on a deployed OpenStack environment. We utilize Gherkin language to write testing scenarios, and Python's Behave library to execute these tests.

## Description

The SCS Health Monitor project aims to ensure the robustness and reliability of OpenStack environments by simulating various scenarios and assessing their performance under different loads. By employing Gherkin language and Behave library, we can define clear, human-readable test cases that cover a wide range of functionalities, from basic system checks to complex stress tests.

## Getting Started

To get started with the SCS Health Monitor project, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies listed in the `requirements.txt` file.
3. Review the existing Gherkin scenarios in the `features` directory to understand the testing coverage.
4. Execute the tests using Behave library to validate the functionality and performance of your OpenStack environment.

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



## Collaborators
- Piotr Bigos [@piobig2871](https://github.com/piobig2871)
- Erik Kostelanský [@Erik-Kostelansky-dNation](https://github.com/Erik-Kostelansky-dNation)
- Katarina Trentau [@fraugable](https://github.com/fraugabel)

## Useful links

### [Openstack python SDK documentation](https://docs.openstack.org/openstacksdk/latest/user/)
### [Openstack CLI tool documentation](https://docs.openstack.org/python-openstackclient/latest/)
### [Parameterisation of tests using scenario outlines](https://jenisys.github.io/behave.example/tutorials/tutorial04.html)
### [Short but concise tutorial on how to setup behave test scenarios](https://behave.readthedocs.io/en/stable/tutorial.html)
