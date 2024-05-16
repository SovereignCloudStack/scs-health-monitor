# Test cases
The purpose of this repository is to provide a tool to test the reliability and performance of the OpenStack API. It creates a real environment with routers, networks, jump hosts, virtual machines (VMs), etc., and collects statistics on API call performance and resource creation times.

## api_monitor.sh for OpenStack script (Original state)
The script currently exists as a [Bash script (api_monitor.sh)](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/main/api_monitor.sh) for testing the OpenStack API's reliability and performance. The original state involves creating a real environment, collecting statistics, and handling failures. However, the script has areas for improvement, such as error handling, verbosity, and optimization.

The script follows these general steps:
1) Creates routers (VPC)
2) Creates networks, subnets and ports (Networks is normally the quantity of AZs)
3) Sets up security groups
4) Create disks from images 
5) Configures virtual IPs and SSH keys
6) Creates jump host VMs and associates floating IPs with them
7) Configures jump hosts for SNAT for outbound traffic and port
8) forwarding for inbound
9) Creates internal VMs distributed across networks and AZs
10) Tests connectivity of VMs to the outside world
11) Cleans up all resources created in reverse order

### Inputs
1) **--debug**         
   - Use set **-x** to print every line executed
2) **-n N**            
   - Number of VMs to create (beyond #AZ JumpHosts)
   - default: 12
3) **-N N**            
   - Number of networks/subnets/jumphosts to create 
   - default: # of AZs in openstack
4) **-l LOGFILE**      
   - Record all commands in LOGFILE
5) **-a N**            
   - Send at most N alarms per iteration 
   - first plus N -1 summarized
6) **-R**       
   - Send recovery email after a completely successful iteration and alarms before
7) **-e ADR**           
   - Sets eMail address for notes/alarms (assumes working MTA)
   - second -e splits eMails; notes go to first, alarms to second eMail
8) **-E**             
   - Exit on error (for CONNTEST)
9)  **-m URN**          
    - Sets notes/alarms by SMN (pass URN of queue)
    - second -m splits notifications; notes to first, alarms to second URN
10) **-s [SH]**         
    - Sends stats as well once per day (or every SH hours), not just alarms
11) **-S [NM]**
    - Sends stats to Grafana via local telegraf http_listener 
    - default for NM=api-monitoring
12) **-q**
    - Do not send any alarms
13) **-d**
    - Boot directly from image (not via volume)
14) **-z SZ**
    - Boots VMs from volume of size SZ
15) **-P**
    - Do not create Port before VM creation
16) **-D**
    - Create all VMs with one API call (
    - implies -d -P
17) **-i N**
    - Sets max number of iterations 
    - default =-1 -> infinite
18) **-r N**
    - Only recreate router after each Nth iteration
19) **-g N**
    - Increase VM volume size by N GB 
    - ignored for -d/-D
20) **-G N**
    - Increase JH volume size by N GB
21) **-w N**
    - Sets error wait (API, VM) 
    - 0 -> inf seconds or negative value for interactive wait
22) **-W N**
    - Sets error wait (VM only)
    - 0 -> inf seconds or negative value for interactive wait
23) **-V N**
    - Set success wait
    - Stop for N seconds (negative value: interactive) before tearing down
24) **-p N**
    - Use a new project every N iterations
25) **-c**
    - NoColors: don't use bold/red/... ASCII sequences
26) **-C**
    - Full connectivity check
    - Every VM pings every other
27) **-o**
    - Translate nova/cinder/neutron/glance into openstack client commands
28) **-O**
    - Like -o, but use token_endpoint auth (after getting token)
29) **-x**
    - Assume exclusive project, clean all floating IPs found
30) **-I**
    - Disassociate floating IPs before deleting them
31) **-L**
    - Create HTTP Loadbalancer (LBaaSv2/octavia) and test it
32) **-LL**
    - Create TCP Loadbalancer (LBaaSv2/octavia) and test it
33) **-LP PROV**
    - Create TCP LB with provider PROV and test it (-LO is short for -LP ovn)
34) **-b**
    - Run a simple compute benchmark
    - It conducts benchmarking operations across multiple VMs in an OpenStack environment and logs the results
    - Specifically, the benchmark calculates the value of pi to 4000 digits
35) **-B**
    - Iterate over each host and conduct [IPerf3 tests](https://iperf.fr/iperf-doc.php)
36) **-t**
    - Long timeouts (2x, multiple times for 3x, 4x, ...)
37) **-T**
    - Assign tags to resources; use to clean up floating IPs
38) **-2**
    - Create secondary subnets and attach secondary NICs to VMs and test
39) **-3**
    - Create secondary subnets, attach, test, reshuffle and retest
40) **-4**
    - Create secondary subnets, reshuffle, attach, test, reshuffle and retest
41) **-R2**
    - Recreate secondary ports after detaching 
    - OpenStack <= Mitaka bug

### Notes

## Gherkin test cases using behave in python (Target state)
The target state involves rewriting the test cases into Gherkin language, a structured way to describe test cases, and implementing them using Behave in Python. This transition would provide several benefits:

- **Structured Test Cases**: Gherkin language provides a structured and human-readable way to describe test scenarios, making it easier to understand and maintain the test cases.

- **Behavior-Driven Development (BDD)**: Behave allows for behavior-driven development, where tests are written based on desired behavior rather than specific implementation details. This promotes collaboration between stakeholders and developers.

- **Python Implementation**: Rewriting the tests in Python using Behave allows for better integration with existing Python codebases, improving maintainability and scalability.

In the target state, each test case described in the Bash script would be translated into a Gherkin scenario and implemented using Behave step definitions in Python. This approach would enhance the clarity, maintainability, and extensibility of the testing framework.

![Tech stack](../assets/img/TechStack.png "Tech stack")

### Inputs
TODO list inputs for test cases in python

### Errors and Updates

For Openstack you can check ports and operational tools by using the command:
`openstack catalog list`
and will get:
```
+-------------+----------------+---------------------------------------------------------+
| Name        | Type           | Endpoints                                               |
+-------------+----------------+---------------------------------------------------------+
| keystone    | identity       | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:5000                              |
|             |                | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:5000     |
|             |                |                                                         |
| designate   | dns            | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:9001                              |
|             |                | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:9001     |
|             |                |                                                         |
| barbican    | key-manager    | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:9311                              |
|             |                | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:9311     |
|             |                |                                                         |
| swift       | object-store   | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:8080/swi |
|             |                | ft/v1/AUTH_476672f1023b4bac8837f95a76881757             |
|             |                | RegionOne                                               |
|             |                |   admin: https://api-int.gx-scs.sovereignit.cloud:8080/ |
|             |                | swift/v1/AUTH_476672f1023b4bac8837f95a76881757          |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-scs.sovereignit.cloud:80 |
|             |                | 80/swift/v1/AUTH_476672f1023b4bac8837f95a76881757       |
|             |                |                                                         |
| nova_legacy | compute_legacy | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:8774/v2/ |
|             |                | 476672f1023b4bac8837f95a76881757                        |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-scs.sovereignit.cloud:87 |
|             |                | 74/v2/476672f1023b4bac8837f95a76881757                  |
|             |                |                                                         |
| neutron     | network        | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:9696                              |
|             |                | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:9696     |
|             |                |                                                         |
| cinderv3    | volumev3       | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:8776/v3/ |
|             |                | 476672f1023b4bac8837f95a76881757                        |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-scs.sovereignit.cloud:87 |
|             |                | 76/v3/476672f1023b4bac8837f95a76881757                  |
|             |                |                                                         |
| nova        | compute        | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:8774/v2.1                         |
|             |                | RegionOne                                               |
|             |                |   public: https://api.gx-                               |
|             |                | scs.sovereignit.cloud:8774/v2.1                         |
|             |                |                                                         |
| heat-cfn    | cloudformation | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:8000/v1  |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:8000/v1                           |
|             |                |                                                         |
| placement   | placement      | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:8780     |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:8780                              |
|             |                |                                                         |
| glance      | image          | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:9292     |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:9292                              |
|             |                |                                                         |
| octavia     | load-balancer  | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:9876     |
|             |                | RegionOne                                               |
|             |                |   internal: https://api-int.gx-                         |
|             |                | scs.sovereignit.cloud:9876                              |
|             |                | RegionOne                                               |
|             |                |   admin: https://api-int.gx-scs.sovereignit.cloud:9876  |
|             |                |                                                         |
| heat        | orchestration  | RegionOne                                               |
|             |                |   internal: https://api-int.gx-scs.sovereignit.cloud:80 |
|             |                | 04/v1/476672f1023b4bac8837f95a76881757                  |
|             |                | RegionOne                                               |
|             |                |   public: https://api.gx-scs.sovereignit.cloud:8004/v1/ |
|             |                | 476672f1023b4bac8837f95a76881757                        |
|             |                |                                                         |
+-------------+----------------+---------------------------------------------------------+
```

this is supposed to be the latest status and the commands for the right tools might not be prompted in the IDE using the openstack SDK. So in case of troubles creating resources etc. it's advised to look for the right commands in the [Documentation](Use new Octavia api for creating Load balancers:
https://docs.openstack.org/openstacksdk/latest).

Like for exemple creating loadbalancers is no longer handled by `neutron`, so the suggested methods lead to an Api-Error, since it is now handled by `octavia` now.
Therefor you have to look for the right methods in the [documentation concerning load_balancer_v2](Use new Octavia api for creating Load balancers:
https://docs.openstack.org/openstacksdk/latest/user/proxies/load_balancer_v2.html
9342064d)