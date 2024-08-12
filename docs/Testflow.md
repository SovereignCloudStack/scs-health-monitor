# Testflow-Infrastructure

## Quick Intro:

* After following the steps to set up the environment including setting up the monitornig, you should be able to start testing with `behave` a testing framwork. On the Cloud-Level you have several features that describe Test Scenerios for single components of the Openstack functionality, like the `openstack_create_network.feature`.
So if you want to test whether you are able to create a network you can use that feature like this:
```
behave openstack_create_network.feature
```
or aswell:

```
behavex openstack_create_network.feature
```
and a test on whether you are able to create a network is running.

* If you want to test whether you can create and delete all openstack resources you simply need this command (for `openstack_testflow.feature` includes all the steps from the creation and delition features):
```
behave openstack_testflow.feature
```

* The Use Case for the `openstack_testflow.feature` and all the creation and deletion features is mostly debugging, because to run a whole infrastructure test this is not sadisfying the dependencies of the variouse resources. But you can set some parameters like the quantity of the resources, if you aim to see if you have a certain quota f.e.
To get a more detailed view on the test run you have the option `--no-capture` and you will receive prints or informational logs during the test run.

```
behave --no-capture openstack_create_network.feature
```
* After the run each built resource will be deleted to avoid a `DuplicateResource-Error`. If you should still encounter this Error, you will have to delete the resource in question by hand ether in the *openstack cli tool* or in the *plus cloud open* dashboard. But make sure this resource is not in use!

## Real Testing:

* As we provide an automated Infrastructure Testing the real deal lies in the `openstack_benchmark_build_infra.feature`. This Feature is creating all resources and configures them in order to build a complete infrastructure with virtual machine (vm) networks that are accessible through jumphosts (jh) that get certain floating ip and allow a port forwarding to the vms. That means it automatically sets up the ssh-access and the security group rules and makes sure applications like `iperf3` are installed on the hosts. This infrastructure emulates a common openstack infrastructure and allows to run a number of benchmark tests to see whether it has the needed capacity.

* You start an infrastructure test by:
```
behave openstack_benchmark_build_infra.feature
```
or aswell:

```
behavex openstack_benchmark_build_infra.feature
```
* It will take some time but you can follow allong, if the infrastructure is builds up successfully.
After the run it deletes all resources.

* If you want run benchmarktests (which is the main goal of this approach), you will have to run the benchmark features together with the `openstack_benchmark_build_infra.feature` like so:
```
behave openstack_benchmark_build_infra.feature cloud_level_testing/features/openstack_benchmark_iperf3.feature cloud_level_testing/features/openstack_benchmark_pingVM.feature cloud_level_testing/features/openstack_benchmark_4000pi.feature
```
The first feature always has to be the `openstack_benchmark_build_infra.feature`. After that you can use the other features, as they only depend on the infrastructure, they don't need to follow a special order.

* Note all features that fail and have a `@create` or `@delete` tag assigned to them will lead to a deletion of the build up resources right after the feature run. Hence if they are followed by a feature depending on those resources this feature will inevitably fail.

## 


