# Testflow-Infrastructure

## Quick Intro:

* After following the steps to set up the environment including setting up the monitornig, you should be able to start testing with `./scs-health-monitor behave` a testing framwork. On the Cloud-Level you have several features that describe Test Scenerios for single components of the Openstack functionality, like the `openstack_create_network.feature`.
So if you want to test whether you are able to create a network you can use that feature like this:
```
./scs-health-monitor behave openstack_create_network.feature
```
or aswell:

```
./scs-health-monitor behavex openstack_create_network.feature
```
and a test on whether you are able to create a network is running.

* If you want to test whether you can create and delete all openstack resources you simply need this command (for `openstack_testflow.feature` includes all the steps from the creation and delition features):
```
./scs-health-monitor behave openstack_testflow.feature
```

* The Use Case for the `openstack_testflow.feature` and all the creation and deletion features is mostly debugging, because to run a whole infrastructure test this is not sadisfying the dependencies of the variouse resources. But you can set some parameters like the quantity of the resources, if you aim to see if you have a certain quota f.e.
To get a more detailed view on the test run you have the option `--no-capture` and you will receive prints or informational logs during the test run.

```
./scs-health-monitor behave --no-capture openstack_create_network.feature
```
* After the run each built resource will be deleted to avoid a `DuplicateResource-Error`. If you should still encounter this Error, you will have to delete the resource in question by hand ether in the *openstack cli tool* or in the *plus cloud open* dashboard. But make sure this resource is not in use!

## Real Testing:

* As we provide an automated Infrastructure Testing the real deal lies in the `openstack_benchmark_build_infra.feature`. This Feature is creating all resources and configures them in order to build a complete infrastructure with virtual machine (vm) networks that are accessible through jumphosts (jh) that get certain floating ip and allow a port forwarding to the vms. That means it automatically sets up the ssh-access and the security group rules and makes sure applications like `iperf3` are installed on the hosts. This infrastructure emulates a common openstack infrastructure and allows to run a number of benchmark tests to see whether it has the needed capacity.

* You start an infrastructure test by:
```
./scs-health-monitor behave openstack_benchmark_build_infra.feature
```
or aswell:

```
./scs-health-monitor behavex openstack_benchmark_build_infra.feature
```
* It will take some time but you can follow allong, if the infrastructure is builds up successfully.
After the run it deletes all resources.

* If you want run benchmarktests (which is the main goal of this approach), you will have to run the benchmark features together with the `openstack_benchmark_build_infra.feature` like so:
```
./scs-health-monitor behave openstack_benchmark_build_infra.feature cloud_level_testing/features/openstack_benchmark_iperf3.feature cloud_level_testing/features/openstack_benchmark_pingVM.feature cloud_level_testing/features/openstack_benchmark_4000pi.feature
```
The first feature always has to be the `openstack_benchmark_build_infra.feature`. After that you can use the other features, as they only depend on the infrastructure, they don't need to follow a special order.

* Note all features that fail and have a `@create` or `@delete` tag assigned to them will lead to a deletion of the build up resources right after the feature run. Hence if they are followed by a feature depending on those resources this feature will inevitably fail.

## Extended Description:

* Our approach to use the behave-framework to build up and test an openstack infrastructure automated relies on certain peculiarities of this framework. First of all you have to understand the basic entities of a testrun:

1. 1 testrun can contain multiple features\
1 feature can contain multiple steps\
1 step can contain multiple substeps


1. In the `environment.py` you can define what actions have to be done \
`before_all` (in the beginning of the testrun), \
`after_feature` (after every feature) and \
`after_all` (in the end of the testrun)\
To calculate for exemple the total duration of the run we set the timer in the `before_all` section and get the result in the `after_all` section, where we also collect the metrics and push them to the prometheus gateway or delete all resources. In the `after_feature` section, we delete ressources if a creation or deletion feature has failed.

1. We tried to keep the steps and features as independent and self contained as possible. But in an infrastructure this is almost impossible, if you don't want to create monolytic steps and functions. Therefore we create an oblect called `context` and an object called `Collector` in the `before_all` section. We store every information, that has to be passed between the steps into the context like the connection to the openstack client. The Collector fetches each resource-id, when a resource is created to ensure that all and only resources that were created in the test run are deleted in the end.

1. However, if we run features, that rely on another feature like on the  `openstack_benchmark_build_infra.feature` the problem occures that the context attributes that are created during a feature run are deleted after each feature. Therefore we created a SharedContext Object that is already initialised `before_all` and stores the data that is necessary for the following features like the test-prefix (context.test_name) and the floating ip and portforwarding (context.redirs).\
So in the end of `openstack_benchmark_build_infra.feature` the following step must be performed: ```Then I can pass the context to another feature``` (to store the needed information into the `SharedContext`)
and the following features have to begin with the step: ``` Given I can get the shared context from previouse feature``` (to transfer the shared informations into the new `context` object). 

## Scaling the Benchmark Infrastructure

First of all is the scale of the benchmark infrastructure highly dependent on the amount of **availability zones** in the project. The number of **availability zones determines how many jumphosts (jhs)** and networks are built. If there are for example two availbility zones, two jumphosts are created and and attached to a floating ip each.\ 
The jumphosts are connected through a shared network but each of them is also **attached to another network of virtual machines (vms)**. The **quantity of vms** can be adjusted in the table of `openstack_benchmark_build_infra.feature`. The vms can be reached from outside the network via port forwarding. Which is enabled by the jh. You can reach the vms by addressing the floating ip of the associated jh and the port number.
The range of the port numbers can also be specified in the `openstack_benchmark_build_infra.feature` the default range is set from 222 to 229.\
Apart from that, you cannot change quantities because the infrastructure automatically adjusts in scale depending on the dependencies.
