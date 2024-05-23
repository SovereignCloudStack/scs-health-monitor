# METRIC OVERVIEW

This is an overview on the metrics, that are supposed to be monitored and presented based on the [api_monitor.sh](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh) and the connected [grafana dashboard](https://github.com/SovereignCloudStack/openstack-health-monitor/tree/main/dashboard). The first table explains the grafana-variables that enable the dashboard to be dynamic as they present keys to be filtered by the user in order to specify the results.

The next table presents the metrics of the actual dashboard panels and their InfluxDB-Query, which has to be translated into PromQL for we are using prometheus for pushing and scraping metrics.

below that we find the Varible-Tables, that explain the keys and tags (in PromQL: labels) created in the api_monitor.sh to add more information to the metrics like making them seperable and provide more informations. It is explained how and where these keys are generated in the source code. As the gneration of these monitoring keys and tags is highly connected to the functional part of the testing this is an approach to breakdown the source code and deliver a look up table in order to create the new testing modules in the behavoir driven design.

Therefore the parent or root functions for all the creation, deletion and waiting functions in the source code are explained in the last section of this documentation.
Finally the main loop is also analized, focussing on the relevant functions that are needed to generate the statistics, like the wait-functions.

## Variables

|Metric/Label|	Description |	Variable |	Exemples|
|----------|----------|----------|----------|
|Clouds	|cloud to be picked	|$mycloud	|see Table CLOUDS |
|Commands	|command to seperate f.e. ssh from api-call	|$mycmd	|see Table COMMANDS |
|Methods	|from command: certain command domains (boot, create, delete)	|$mymethod	|see Table METHODS|
|Resources |from command: certain commands with the Prefix `wait`|$mywait	|see Table RESOURCES|
|Benchmarks |from command: certain commands that are part of benchmark functions |$mybench |see Table BENCHMARKS|


## Grafana-Dashboard				
|Metric	|Description	|Variable	|Unit	|Influx Query	|Exemple Endpoints|
|---------|----------|----------|----------|----------|----------|
|OVERVIEW	||||||				
|API calls	|Takes all connections(with return code) from selected cloud with selected command, method in current time interval	|return-code, $mycloud, $mycmd, $mymethod	|count	|` SELECT count("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval) fill(null)`| |
|API errors	|Takes all connections(with error return code) from selected cloud with selected command, method in current time interval 	|return-code, $mycloud, $mycmd, $mymethod	|count	|`SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval)` ||
|API success rate	|Takes all connections subtracts the sum of counts with an error-return code and devides it through all connections filtered by selected cloud with selected command, method in current time interval | return-code, $mycloud, $mycmd, $mymethod	|percent	|`SELECT ((count("return_code")-sum("return_code"))/count("return_code")) FROM "$mycloud" WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter`||	
|ssh conns	|Takes all connections(with return code) and the command ssh from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|count	|`SELECT count("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" = 'ssh') AND $timeFilter GROUP BY time($__interval) fill(null)`|
|ssh errors	|Takes all connections with an error return code and the command ssh from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod|	count	|`SELECT sum("return_code") FROM "$mycloud" WHERE ("cmd" = 'ssh') AND $timeFilter GROUP BY time($__interval)`||
|ssh success rate	|Takes all connections with cmd=ssh subtracts the sum of cmd=ssh-counts with an error-return code and devides it through all connections with cmd=ssh filtered by selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|percent	|`SELECT ((count("return_code")-sum("return_code"))/count("return_code")) FROM "$mycloud" WHERE ("cmd" = 'ssh') AND $timeFilter`||
|Resources	|Takes all connections(with return code) and the commands that match the RESOURCES-list in the $mywait-Variable from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|count	|`SELECT count("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mywait$/) AND $timeFilter GROUP BY time($__interval) fill(null)`|	
|Resource errors	|Takes all connections with an error return code and the commands that match the RESOURCES-list in the $mywait-Variable from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|count	|`SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mywait$/) AND $timeFilter GROUP BY time($__interval)`||
|iperf success rate	|Takes all connections with cmd=iperf3 subtracts the sum of cmd= iperf3-counts with an error-return code and devides it through all connections with cmd= iperf3 filtered by selected cloud with selected method in current time interval |return-code, $mycloud, $mycmd, $mymethod	|percent	|`SELECT ((count("return_code")-sum("return_code"))/count("return_code")) FROM "$mycloud" WHERE ("cmd" = 'iperf3') AND $timeFilter`||
|STATS ||||||			
|API errors	|Takes all connections with an error return code from selected cloud with selected method in current time interval and grouped by method |return-code,$mycloud, $mycmd, (Group = $mymethod)|	rc	|`SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval), "cmd", "method"	`||
|Resource errors	|Takes all connections with an error return code the commands that match the RESOURCES-list in the $mywait-Variable  from selected cloud with selected method in current time interval and grouped by wait-command ||# errors	|`SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mywait$/) AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)	`|waitDELLBAAS  waitJHVM  waitJHVOLUME  waitLBAAS  WaitVM|
|Bench (ssh) errors	|Takes all connections with an Benchmark-Error (tagged by benchmark functions in shellscript) from selected cloud with selected method in current time interval and  grouped by ERR($tag_cmd) ||Errs	|`SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mybench$/) AND $timeFilter GROUP BY time($__interval), "cmd" fill(null)`|ERR(LBconn)  ERR(totDur)  ERR(4000pi)  ERR(fioBW)  ERR(fioLat10ms)  ERR(fiokIOPS)  ERR(iperf3)  ERR(ping)  ERR(ssh)|
|PERFORMANCE	||||||				
|API response times	|Takes the mean duration from all connections(with return code) from selected cloud with selected command, method in current time interval and groups them by cmd or method||s|`SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval), "cmd", "method" fill(none)`||	
|Resource wait	|Takes the mean duration all connections with the command that match the RESOURCES-list in the $mywait-Variable and the method-tags (A) ACTIVE, (B) available, (C) XDELX (D) the rest from selected cloud with selected method in current time interval and grouped by wait-command ||s |(A) `SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag = 'ACTIVE') AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)` (B) `SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag = 'available') AND $timeFilter GROUP BY time($__interval), "cmd" fthe method-tagill(none)` (C) `SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag = 'XDELX') AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)` (D) `SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag !~ /^(ACTIVE\|available\|XDELX)$/) AND $timeFilter GROUP BY time($__interval), "cmd"::tag, "method"::tag fill(none)` ||
|Bench |Takes the mean duration from all connections(with return code) with commands thatr match the Bench-list in the $mybench-Variable from selected cloud with selected command, method in current time interval and groups them by cmd or method ||s, Gb/s, s, %maxt*10, s*10, MB/s, IO/s, %	|`SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mybench$/) AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)`||


## Variable-Tables

### CLOUDS

* Regex: None

|Cloud-list |Lines in Code |Code |Description|
|----------|----------|----------|----------|
|plus-pco||||
|plus-prod2||||
|plus-prod3||||
|plus-prod4||||
|gx-scs||||
|stackit||||
|wavestack1||||
|cnds||||
|aov||||
|datapoc||||
|ciab||||

### COMMANDS

* Regex: `/^(nova|neutron|glance|cinder|token|catalog|swift|octavia)$/`
* Tag/Label: `cmd`/`command`

|Command-list	| `method` |Lines in Code |Description|
|----------|----------|----------|----------|
|All||||
|catalog ||||
|cinder ||||
|glance ||||
|neutron ||||
|nova ||||
|octavia ||||
|swift ||||
|token ||||

### METHODS

* Regex:
* Tag/Label: cmd/command

	
|Method-list |`method`|Lines in Code|Description|
|----------|----------|----------|----------|	
|All ||||
|boot||||
|console-log
|create |`createNets()` `createResources()`|[L1742-L1752](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1742-L1752)| orchestrates the creation of networks, handling any errors that may occur during the process and returning an appropriate error code: initializes the `ERC` variable to zero, used to track any errors that occur during the network creation process. Then it calls the `createResources`function to create the single `JHNET`-network `${RPRE}NET_JH` and assigns the output to `ERC`, if successful. If an error occurs, `ERC` is updated with the error code. Then it checks if the number of availability zones `NONAZS` is less than or equal to one. If `true`, it creates networks for each VM `NONETS` without specifying any availability zones. If `false`, it creates networks for each virtual machine and specifies the availability zone hint based on the array `NAZS`. Then returns the final error code ERC to indicate the success or failure of the network creation process.
|| `createJHVols()` `createResources()`|[L1989-L1993](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1989-L1993)| responsible for creating Cinder volumes: initializes an array `JVOLSTIME=()` to store timestamps related to the creation of Cinder volumes and calls the `createResources` function with several arguments to create Cinder volumes using the cinder create command: `$NOAZS` (Number of availability zones), `VOLSTATS` (statistics related to volume status), `JHVOLUME` (prefix for the vol name), `NONE` (placeholder), `JVOLSTIME` (array of timestamps) `id` (column to retrieve the vol ID), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder create` command to create the volume specifies the image ID `$JHIMGID`, availability zone, vol name and vol size `$JHVOLSIZE`. The vol name is constructed using the prefix `${RPRE}RootVol_JH` followed by an index `$no`| creates networks for both the Jump Host and VMs in the OpenStack environment, handles any errors and returns exit codes by caslling the `createResources` function to create a network for the JH and specifing the following parameters: `1` (number of networks to create), `NETSTATS` (statistics related to network status), `JHNET` (prefix for the network name), `NONE` (placeholder), `id` (column to retrieve the network ID), `$NETTIMEOUT` (timeout value for the operation), `neutron net-create "${RPRE}NET_JH"`is the actual `neutron` command to create the network for the JH constructing the network name using the prefix `${RPRE}NET_JH`. Then the creation of networks for VM is handled with an if statementthat checks whether there is only one availability zone (NONAZS <= 1) so it would not specify an availability zone hint. Else it specifies an availability zone hint based on the available availability zones. The return `$ERC` statement returns the value that indicates whether any errors occurred during the network creation process|
||`createVols()` `createResources()`|[L2008-L2013](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2008-L2013)| creates Cinder volumes for virtual machines, except when the virtual machines are booted from an image therefore it checks if the variable `$BOOTFROMIMAGE` is not empty, which would mean the virtual machines should be booted from an image, so the function immediately returns without creating volumes. `VOLSTIME=()` initializes an array to store timestamps related to the creation of Cinder volumes and calls the `createResources` function with several arguments: `$NOVMS` (number of virtual machines), `VOLSTATS` (statistics related to vol status), `VOLUME` (prefix for the vol name),`NONE` (placeholder), `VOLSTIME` (array to store timestamps), `id` (column to retrieve the vol ID), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder create` command specifies the image ID `$IMGID`, availability zone, vol name and vol size `$VOLSIZE`. The vol name is constructed using the prefix `${RPRE}RootVol_VM` followed by an index `$no`|
|delete |`deleteNets()` `deleteResources()`|[L1754-L1761](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1754-L1761)|handles the deletion of networks in the OpenStack environment, including main network for VMs and any secondary networks if specified. It checks if the variable `$SECONDNET` is not empty, which means there is a secondary network that needs to be deleted, so it proceeds with deleting it by calling the `deleteResources` function to delete the secondary network. The following parameters are specified: `NETSTATS` (statistics related to network status), `SECONDNET` (prefix for the secondary network name), `""` (placeholder), `$NETTIMEOUT` (timeout value for the operation). The actual `neutron net-delete` command deletes the network.
||`deleteJHVols()` `deleteResources()`|[L2003-L2006 ](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2003-L2006)|deletes Cinder volumes that match the specified prefix for the volume name `JHVOLUME` by calling the  `deleteResources` function with several arguments and using the cinder delete command: `VOLSTATS` (statistics related to volume status), `JHVOLUME` (prefix for the volume name),`""`(placeholder), `$CINDERTIMEOUT` (timeout value for the operation), `cinder delete` to delete the volumes|
||`deleteVols()` `deleteResources()`|[L2024-L2028](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2024-L2028)|deletes Cinder volumes associated with virtual machines, unless the virtual machines are configured to boot from an image than it returns without performing any deletion checks if the variable $BOOTFROMIMAGE is not empty. If it is not empty, it means the virtual machines are configured to boot from an image, so the function returns early without attempting to delete volumes. It calls the `deleteResources` function with several arguments: `VOLSTATS` (statistics related to vol status), `VOLUME` (prefix for the vol name), `""` (placeholder), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder delete` command deletes the volumes|
|flavor-show
|floatingip-create | `SNATROUTE=""` `createFIPs()` `neutron floatingip-create` `neutron floatingip-list`| [L2080-L2128](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2080-L2128) |automates the process of creating Floating IPs `FIPs` and setting routes via a Virtual IP `VIP`. Initializes `$SNATROUTE` as local variable to an empty string before hand. Then checks for Port Ownership: if `$FIPWAITPORTDEVOWNER` is set, it waits for `JHPORTS` to have a device owner before proceeding, because the ports need to be created and assigned to a VM before associating a FIP. The `FIPs` are created `neutron floatingip-create` command. If the creation fails or if `$INJECTFIPERR` is set, the func returns with an error. Next the VIP is retrieved from the router's external gateway information and it is determened if `SNAT` is enabled on the router. If disabled, it updates the router's routes to use the VIP as the next hop. If SNAT is enabled, proceeds and prints that no action is needed. `$SNATROUTE` is then set to indicate whether setting the route via SNAT gateways was successful. By using `neutron floatingip-list` the FIPs associated with the ports are extracted and stored in the `FLOAT` variable and added to the `FLOATS` array. The list of FIPs is printed as an output.
|floatingip-delete |`deleteFIPs()` `neutron floatingip-disassociate` `neutron floatingip-delete`| [L2130-L2160](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2130-L2160)| ensures that both the VIP nexthop configuration and associated FIPs are properly cleaned up, retries operations to ensure that resources are properly removed and handles potential errors. `$SNATROUTE` is set (indicating that the route via VIP nexthop was previously configured) and there is a router `${ROUTERS[0]}`, it attempts to update the router configuration to remove all routes `--no-routes`. If this fails, it retries after a brief delay. If `$DISASSOC` is set (indicating a need to disassociate FIPs before deletion, possibly due to a bug?) it stores the list of existing FIPs (OLDFIPS) then uses the `neutron floatingip-disassociate` command for disassociation. Finally the `neutron floatingip-delete` command is used to delete the FIPs. To ensure that all FIPs are properly deleted this is retried. If any FIPs remain after deletion, a warning is logged and retried to delete again.
|floatingip-list
|image-show
|issue
|keypair-add | `createKeypairs_old()` `createKeyPair()` `createKeypairs()`| [L2030-L2065](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2030-L2065)|`createKeypairs_old()`: generates two key pairs using the nova keypair-add command. It sets a stricter umask before creating the key pairs to ensure that the permissions on the generated private key files are limited. The generated private keys are saved to files in the specified directory (`$DATADIR`). The names of the key pairs are `${RPRE}Keypair_JH` and `${RPRE}Keypair_VM`. The names of the key pairs are stored in the `KEYPAIRS` array for later use.`createKeyPair()`: This function creates a single key pair. If the corresponding public key file does not exist in the specified directory (`$DATADIR`), it generates a new key pair using ssh-keygen. It then uses nova keypair-add to upload the public key to OpenStack. If the key pair creation fails, it attempts to delete any existing key pair with the same name and returns an error. `createKeypairs()`: This function orchestrates the creation of key pairs. It first prints a message indicating that new key pairs are being created. Then, it calls createKeyPair twice, once for each key pair (`${RPRE}Keypair_JH` and `${RPRE}Keypair_VM`). If the creation of either key pair fails, it prints an error message and returns a non-zero exit status. Otherwise, it prints a newline to indicate the completion of the key pair creation process.
|keypair-delete |`deleteKeypairs()` `deleteResources()`|[L2067-L2073](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2067-L2073)| `deleteKeypairs()` is responsible for deleting key pairs from the OpenStack environment. It utilizes the `deleteResources` function to delete key pairs using the nova keypair-delete command. The function takes care of deleting all key pairs associated with the specified prefix `${RPRE}`. Additionally, it may include commands to remove the corresponding private key files (commented out in this snippet).
|keypair-list
|lbaas-healthmonitor-create
|lbaas-healthmonitor-delete
|lbaas-listener-create
|lbaas-listener-delete
|lbaas-loadbalancer-create
|lbaas-loadbalancer-delete
|lbaas-loadbalancer-list
|lbaas-loadbalancer-show
|lbaas-member-create
|lbaas-member-delete
|lbaas-pool-create
|lbaas-pool-delete
|lbaas-pool-show
|list
|meta
|net-create
|net-delete
|net-external-list
|port-create|`createJHPorts()` `createResources()`|[L1942-L1955](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1942-L1955)|  creates ports for JHs and sets allowed address pairs for each port to control traffic flow. uses`createResources()`. The number of ports created is determined by the value of `$NOAZS` (number of availability zones). It assigns security groups to the ports using `${SGROUPS[0]}`. names the ports using a combination of `${RPRE}`, `"Port_JH\${no}"`(`${no}` index of the availability zone). It iterates over each port to create it and then call `ostackcmd_id` to update the port with allowed address pairs.allowed address pairs are set to 0.0.0.0/1 and 128.0.0.0/1, traffic from these IP ranges is allowed. assigns the ports to a specific network using `${JHNETS[0]}`.
||`createPorts()` `createResources()`|[L1957-L1962](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1957-L1962)|creates ports for VMs based on previously specified conditions and configurations. Checks if the variable `$MANUALPORTSETUP` is set. If so proceeds to create ports; otherwise, it skips port creation. uses the `createResources()` parent function. `$NOVMS` determines the number of ports to create. Security groups are assigned to the ports using `${SGROUPS[1]}`. The ports are named using a combination of `${RPRE}`, `"Port_VM${no}"` (`${no}` index of VM).Assigns the ports to networks using `"\${NETS[\$((\$no%$NONETS))]}"` (`${NONETS}` number of networks)|
||`create2ndPorts()` `createResources()` `neutron port-delete`|[L1964-L1970](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1964-L1970)|
|port-delete|`deleteJHPorts()` `deleteResources()`| [L1972-L1975](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1972-L1975)|deletes the JH associated ports using the OpenStack command `neutron port-delete`. Uses `deleteResources()` passing the following arguments: `NETSTATS` (name of the timing statistics array), `JHPORT` (name of the array containing the ports), `""` (name of the array to store timestamps - might not be needed here), `$NETTIMEOUT` (timeout value for the deletion operation), `neutron port-delete` (OpenStack command),any errors encountered during port deletion are handled internally by `deleteResources()`
||`deletePorts()` `deleteResources()`|[L1977-L1980](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1977-L1980)||
||`delete2ndPorts()` `deleteResources()`|[L1982-L1987](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1982-L1987)| 
|port-list
|port-show
|port-update
|rename
|router-create
|router-delete|||


### RESOURCES	

* Regex:	`/^wait/` 
* Tag/Label: `cmd`/`command`
* Parnet Functions: `waitlistResources()` and `handleWaitErr()`

	└── Arguments: `STATNM RSRCNM CSTAT STIME PROG1 PROG2 FIELD COMMAND`

|Resource-list |`method`|Lines in Code| Description |
|----------|----------|----------|----------|	
|All	||||
|waitDELLBAAS| see `waitdelLBs()`
|waitJHPORT
|waitJHVM
|waitJHVOLUME |`waitJHVols()`|[L1996-L2001](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1996-L2001)|  calls the `waitlistResources` function with several arguments and this function waits for Cinder volumes to reach a specific state `available` before proceeding. the funcion uses the cinder list command to check the status of volumes. After waiting for the volumes, the `handleWaitErr` function is called, where arguments such as the label `"JH volumes"`, statistics related to volume status, a timeout value are passed and the command `cinder show`. this is how any errors that occur during the waiting process are handled.
|waitLBAAS ||[L457-L461](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L457-L461)|checks if both the variables `$OPENSTACKCLIENT` and `$LOADBALANCER` are not empty. If they are not empty, it uses the `openstack loadbalancer member create --help` command to check if the `--wait` option is available. If the `--wait` option is found, it sets the variable `$LBWAIT` to `"--wait"`. This variable can be used later to control the behavior of a subsequent command related to load balancer member creation.
||`waitLBs()` `waitlistResources()` `neutron lbaas-loadbalancer-list()` `handleWaitErr()`| [L2483-L2493](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2483-L2493)| related to waiting for LBs, ensuring that they are properly provisioned. It waits for LBs to reach the `"ACTIVE"` state. takes an optional argument `--nostat` to skip collecting statistics during the wait, if provided. Else `waitlistResources()` is called with the following arguments: `LBSTATS` (timing statistics array), `LBAAS` (array containing LBs), `LBCSTATS` (array to collect completion timing stats), `LBSTIME` (array with start times), `"ACTIVE"` (value to wait for), `"NONONO"` (alternative value to wait for), `4` (timeout value), `$NETTIMEOUT`  (timeout value for OpenStack commands), `neutron lbaas-loadbalancer-list` (OpenStack command to list LBs), `handleWaitErr` is called if any errors encountered during the wait.
|| `waitdelLBs()` `waitlistResources()` `neutron lbaas-loadbalancer-list()`| [L2495-L2501](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2495-L2501)| waits for LBs to be deleted. checks if there are LBs to delete (`DELLBAASS` array is not empty) and calls `waitlistResources()` to delete LBs with following arguments: `LBSTATS` (timing statistics array), `DELLBAASS` (array containing LBs to delete), `LBDSTATS` (array to collect completion timing stats), `LBDTIME` (array with start times), `"XDELX"`(value to wait for -> indicating deletion), `$FORCEDEL` (optional to force deletion), `2` (timeout value), `$NETTIMEOUT` (timeout value for OpenStack commands), `neutron lbaas-loadbalancer-list` (OpenStack command to list LBs)
|waitVM
|waitVols|`waitVols()`|[L2016-L2022](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2016-L2022)| ensures that Cinder volumes are available before proceeding with further actions, unless the VMs are configured to boot from an image by checking if the variable `$BOOTFROMIMAGE` is not empty, which would mean the VMs are configured to boot from an image and the func returns early without waiting for volumes, otherwise it calls the `waitlistResources` function with several arguments and waits for Cinder volumes to reach the `available` state before proceeding. The actual `cinder list` command is used to check the status of vols. If any errors occur during the waiting process the `handleWaitErr` function is called and the label `Volumes`, statistics related to vol status, a timeout value, and the `cinder show` command are passed


### BENCHMARKS

* Regex:	```/^(4000pi|iperf3|ssh|totDur|LBconn|ping|fioBW|fiokIOPS|fioLat10ms)$/```
* Tag/Label:	cmd / command

| Benchmark-list | `method` | `duration` | `return_code` | Lines in Code | Description | Progress |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|			
|All |||
| 4000pi| (`JHVM$JHNO`) *TODO* | (`$BENCH`) *TODO* | `0`| [L3242-L3262](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3242-L3262) | On each JumpHost VM (var `$NOAZS`) calculate 4k digits of Pi (`{ TIMEFORMAT=%2U; time echo 'scale=4000; 4*a(1)' \| bc -l; }`) and measure time. Write result to log file.| 0 % |
| LBconn	| Number of VMs to create (beyond #AZ JumpHosts, def: 12) (`$NOVMS`) | Total duration of sending all requests | | [L2598-L2612](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2598-L2612), (the same in [L2628-L2642](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2628-L2642) ) | For the number of LBs (var `$NOVMS`) send the request `curl -m4 http://$LBIP/hostname 2>/dev/null` and measure the total duration. Round Robin -> each server gets one request. Send duration (and possible errors) to Telegraf. | 45 % |
| fioBW |||||| 0 %|
| fioLat10ms|||||| 0 %|
| fiokIOPS |||||| 0 %|
| iperf3 | *TODO* (`s$VM`) | *TODO* (`s$VM`)| 0 | [L3426-L3494](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3426-L3494)| performs iperf3 tests between multiple hosts (var `$NONETS`). It iterates through each pair of source and target hosts, connects to each target host, and runs iperf3 tests to measure the network bandwidth, CPU utilization, and other metrics. The results are then displayed and optionally logged. Additionally handles retries if the initial test fails| 0 %|
| ping | `stats` | `$FPRETRY`| `$FPERR` | [L4203-L4205](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4203-L4205), [L4219-L4220](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4219-L4220), [L4373-L4384](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4373-L4384), [L4385-L4391](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4385-L4391) | Execute function [fullconntest()](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3346-L3424) which performs connectivity tests. Each VM pings each VM. FPRETRY: Number of retried pings, FPERR: Number of failed pings| 20 % |
| ping| `errors`| `1`| `$FPERR` | [L4215](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4215)| See above | 20 % |
| ping | `retries`| `1` | `$FPRETRY`| [L4216](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4216)| See above | 20 % |
| ssh (in function wait222)	    | `JHVM$JHNO` (var `$JHNO` is idx of jump host in `$NOAZS`) | Duration of pinging one jump host | Number of jump hosts unable to ping | [L3016-L3049](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3016-L3049) | Ping each JumpHost VM (var `$NOAZS`) and measure duration this took, including errors. Then test if ssh port is reachable via netcat. | 0 % |
| ssh (in function wait222) | `VM$JHNO:$pno` (var $pno is port number) | Duration since calling `wait222` (including ssh test above) until logging this message (L3092) | `1` if netcat connection attempt timed out; `0` otherwise | [L3016-L3096](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3016-L3096) | For each JumpHost iterate over each VM (port forwarding rule `REDIRS`: `${REDIRS[$JHNO]}`) and try to access port number (`pno`) by executing netcat (`nc $NCPROXY -w 2 ${FLOATS[$JHNO]} $pno`). (If netcat took too long (`$ctr -ge $MAXWAIT`), check status of VM by calling OpenStack Nova. If `provisioning_status` is not `ACTIVE`, send alarm.)|  0 % |
| ssh (in function testjhinet)	 | `JHVM$JHNO` | Duration it takes for executing the tasks for one JumpHost | Return code of `testlsandping()`: `1`: ping failed; `2`: ls or user_data injection failed | [L3185-L3220](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3185-L3220)| For each JumpHost perform ping test against the host itself and call `[testlsandping()](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3103)` which tests ssh and internet ping.| 0 % |
| totDur | Max cycle time (`$MAXCYC`), an calculated upper bound (including magic numbers) how long one iteration may take depending on the tasks which are performed | Relative performance (`$RELPERF`) | Number of slow iterations, which is incremented by one when `$THISRUNTIME` is greater than `$MAXCYC` | [L4455-L4484](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4455-L4484) | Log measured relative duration of current iteration (var `$RELPERF`, relative performance/time; calculated `echo "scale=2; 10*$THISRUNTIME/$MAXCYC" \| bc -l`). Send alert if performance of one cycle is slow. See commit [7fa38](https://github.com/SovereignCloudStack/openstack-health-monitor/commit/7fa38f9f86280bc409783e81c7b6cd0345dca530). FYI: `$TOTTIME` is the overall runtime summing up all iterations and is present in overall stats. |	 0 % |		

## Parent Functions

### ostackcmd_id()
* Lines in Code: [L1024-L1080](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1024-L1080)  
* Purpose: provide a comprehensive wrapper for executing OpenStack commands with timeout enforcement, error handling, logging, and status extraction capabilities
* Description:
  - parameters:
    - `$1` The ID to extract from the command output
    - `$2` Timeout for the command execution (in seconds)
    - `$3`oo: The actual OpenStack command to execute
  - records the start time of the command execution
  - executes the specified OpenStack command using the mytimeout function to enforce the provided timeout
  - captures the command response and determines the command's return code
  - logs the command execution details including start time, end time, ID, status, command, return code, and response to a logfile
  - if the command fails and error reporting is enabled, it sends an alarm notification and waits for a specified duration before retrying.
  - if the command fails due to HTTP 409 conflict, it retries the command after a brief delay.
  - extracts the ID and status from the command output based on the provided ID name.
  - checks if the execution time exceeds a threshold and logs a warning if it does.
  - returns a string containing the execution time, ID, and status of the command.
* Dependencies: relies on the external functions: `translate`, `mytimeout`, `log_grafana`, `sendalarm` and `errwait` for translating commands, enforcing timeouts, logging, error handling, and alarm notification

* Code:
```
# Command wrapper for openstack commands
# Collecting timing, logging, and extracting id
# $1 = id to extract
# $2 = timeout (in s)
# $3-oo => command
# Return value: Error from command
# Output: "TIME ID STATUS"
ostackcmd_id()
{
  local IDNM=$1; shift
  local TIMEOUT=$1; shift
  if test $TIMEOUTFACT -gt 1; then let TIMEOUT*=$TIMEOUTFACT; fi
  local LSTART=$(date +%s.%3N)
  translate "$@"
  RESP=$(mytimeout $TIMEOUT ${OSTACKCMD[@]} 2>&1)
  local RC=$?
  local LEND=$(date +%s.%3N)
  local TIM=$(math "%.2f" "$LEND-$LSTART")

  test "$1" = "openstack" -o "$1" = "myopenstack" && shift
  CMD="$1"
  if test "$CMD" = "neutron" -a "${2:0:5}" = "lbaas"; then CMD=octavia; fi
  log_grafana "$CMD" "$2" "$TIM" "" "$RC"
  if test $RC != 0 -a -z "$IGNORE_ERRORS"; then
    sendalarm $RC "$*" "$RESP" $TIMEOUT
    errwait $ERRWAIT
  fi

  # Retry if we have a HTTP 409
  if test $RC = 1 -a -z "$NORETRY" && echo "$RESP" | grep '(HTTP 409)' >/dev/null 2>&1; then
    sleep 5
    LSTART=$(date +%s.%3N)
    RESP=$(mytimeout $TIMEOUT ${OSTACKCMD[@]} 2>&1)
    local RC=$?
    local LEND=$(date +%s.%3N)
    local TIM=$(math "%.2f" "$LEND-$LSTART")
    log_grafana "$MCD" "$2" "$TIM" "" "$RC"
    if test $RC != 0 -a -z "$IGNORE_ERRORS"; then
      sendalarm $RC "$*" "$RESP" $TIMEOUT
      errwait $ERRWAIT
    fi
  fi

  STATUS=$(echo "$RESP" | grep "^| *status *|" | sed -e "s/^| *status *| *\([^|]*\).*\$/\1/" -e 's/ *$//')
  if test -z "$STATUS"; then STATUS=$(echo "$RESP" | grep "^| *provisioning_status *|" | sed -e "s/^| *provisioning_status *| *\([^|]*\).*\$/\1/" -e 's/ *$//'); fi
  if test "$IDNM" = "DELETE"; then
    ID="$STATUS"
    echo "$LSTART/$LEND/$ID/$STATUS: ${OSTACKCMD[@]} => $RC ($STATUS) $RESP" >> $LOGFILE
  else
    ID=$(echo "$RESP" | grep "^| *$IDNM *|" | sed -e "s/^| *$IDNM *| *\([^|]*\).*\$/\1/" -e 's/ *$//')
    echo "$LSTART/$LEND/$ID/$STATUS: ${OSTACKCMD[@]} => $RC ($ID:$STATUS) $RESP" >> $LOGFILE
    if test "$RC" != "0" -a -z "$IGNORE_ERRORS"; then echo "$TIM $RC"; echo -e "${YELLOW}ERROR: ${OSTACKCMD[@]} => $RC $RESP$NORM" 1>&2; return $RC; fi
  fi
  if test "${TIM%.*}" -gt $((3+$TIMEOUT/4)); then echo -e "${YELLOW}Slow ${TIM}s: ${OSTACKCMD[@]} => $RC $RESP$NORM" 1>&2; fi
  echo "$TIM $ID $STATUS"
  return $RC
}
```

### ostackcmd_tm_retry-Versions
* Lines in Code: L1145-L1176 [link:https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1145-L1176]
* Purpose: provide helper functions and variables
* Description
  - break down:
    - `ostackcmd_tm_retry_N()` retries executing a reentrant OpenStack command a specified number of times `$NORETRY` with a `2-second sleep` interval between retries. It takes the same parameters as `ostackcmd_tm()`. If the command succeeds `$RRC == 0`, it returns `0`, otherwise, it returns the command's return code `$RRC`.
    - `ostackcmd_tm_retry()`: a wrapper around `ostackcmd_tm_retry_N()`, setting the number of retries to `2` by `default`
    - `ostackcmd_tm_retry3()`: similar to `ostackcmd_tm_retry()`, but it retries the command `3` times

* Code:

```
# ostackcmd_tm with a retry after 2s (idempotent commands only)
ostackcmd_tm_retry_N()
{
  local NORETRY=$1
  local RESLEEP=2
  local RECTR=0
  local RRC=0
  shift
  while test $RECTR -lt $NORETRY; do
    ostackcmd_tm "$@"
    local RRC=$?
    if test $RRC = 0; then return 0; fi
    sleep $RESLEEP
    let RESLEEP+=1
    let RECTR+=1
  done
  return $RRC
}

# ostackcmd_tm with a retry after 2s (idempotent commands only)
# Parameters: See ostackcmd_tm
ostackcmd_tm_retry()
{
  ostackcmd_tm_retry_N 2 "$@"
}

# ostackcmd_tm with a retry after 2s (idempotent commands only)
# Parameters: See ostackcmd_tm
ostackcmd_tm_retry3()
{
  ostackcmd_tm_retry_N 3 "$@"
}
```
### SCOL, state2col(), STATE, FAIEDNO
* Lines in Code: L1178-L1191 [link:https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1178-L1191]
* Purpose: provide helper functions and variables
* Description
  - break down:
    - `SCOL` variable that holds the color code used for displaying states. It's initially set to an empty string.
    - `state2col()` this function sets the color `SCOL` based on the state passed as an argument `$1`. It checks 
      - if the state is `"ACTIVE"` or `"UP"` and sets `SCOL` to `green`, 
      - if the state is `"BUILD"`, `"PENDING"`, `"creating"`, `"downloading"`, or `"DOWN"`, it sets `SCOL` to `yellow`, 
      - and if the state starts with `"ERROR"` or `"error"`, it sets `SCOL` to `red`.
    - `STATE` variable to store the state of the current operation
    - `FAILEDNO` variable to track the number of failed operations, initially set to 0
* Code:
```
SCOL=""
# Set SCOL according to state in $1
state2col()
{
    SCOL=""
    local STA="$1"
    if test "$STA" == "ACTIVE" -o "$STA" == "active" -o "$STA" == "UP"; then SCOL="$GREEN"
    elif test "$STA" == "BUILD" -o "${STA:0:7}" == "PENDING" -o "$STA" == "creating" -o "$STA" == "downloading" -o "$STA" == "DOWN"; then SCOL="$YELLOW"
    elif test "${STA:0:5}" == "ERROR" -o "${STA:0:5}" == "error"; then SCOL="$RED"
    fi
}

STATE=""
FAILEDNO=0
```
#### colstat

* Lines in Code: [L1392-L1412](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1392-L1412)  
* Purpose: provide a useful function for visualizing status information, especially in command-line interfaces, where colors can convey important information quickly
* Decription:
  - parameters:
    - `$1` Status string to be converted
    - `$2` The desired first status to be highlighted    
    - `$3` Optional, a second desired status to be highlighted
  - Output:
    prints out a one-character string representing the status with colors.
    returns a code:
    - `2` if the status matches either `$2` or `$3`
    - `1` if the status indicates an error
    - `3` if the status is missing
    - `0` if the status is in progress or doesn't match any conditions
  - Color Codes:
    - `Green (*)` indicates a match with `$2` or `$3`, or a `non-null` status
    - `Red` indicates an error status
    - `Default` returns the first character of the status string if no match or error is detected

* Code:
```
# Convert status to colored one-char string
# $1 => status string
# $2 => wanted1
# $3 => wanted2 (optional)
# Return code: 3 == missing, 2 == found, 1 == ERROR, 0 in progress
colstat()
{
  if test "$2" == "NONNULL" -a -n "$1" -a "$1" != "null"; then
    echo -e "${GREEN}*${NORM}"; return 2
  elif test "$2" == "$1" || test -n "$3" -a "$3" == "$1"; then
    echo -e "${GREEN}${1:0:1}${NORM}"; return 2
  elif test "${1:0:5}" == "error" -o "${1:0:5}" == "ERROR"; then
    echo -e "${RED}${1:0:1}${NORM}"; return 1
  elif test -n "$1"; then
    echo "${1:0:1}"
  else
    # Handle empty (error)
    echo "?"; return 3
  fi
  return 0
}
```



### createResources()
* Lines in Code: [L1207-L1252](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1207-L1252)  
* Purpose: provide a flexible way to create and manage resources in an OpenStack environment while tracking their creation progress and handling errors
* Description:
  - parameters:
    - `$1` Quantity of resources to create.
    - `$2` Name of timing statistics array.
    - `$3` Name of resource list array (appended with "S").
    - `$4` Name of another resource list array (appended with "S"). This is optional and can be used to reference additional resources.
    - `$5` Name of yet another resource list array (appended with "S"). This is also optional and can be used to reference more resources.
    - `$6` Name of array where timestamps of the operation are stored (optional).
    - `$7` Name of the ID field from the resource to be used for storing in $3.
    - `$8` Timeout for the operation.
    - `$9-` OpenStack command to be called referencing `$AZ` (1 or 2), `$no` (running number), `$VAL`, and `$MVAL` (from `$4` and `$5`)
  - initializes various variables and arrays to store resource lists and timestamps to manage the creation process
  - loops through the specified quantity of resources, executing the provided OpenStack command for each resource creation
  - updates the status of the resource creation process based on the command's response
  - handles any errors encountered during the creation process and returns an appropriate exit code
  
* Code

```
# Create a number of resources and keep track of them
# $1 => quantity of resources
# $2 => name of timing statistics array
# $3 => name of resource list array ("S" appended)
# $4 => name of resource array ("S" appended, use \$VAL to ref) (optional)
# $5 => dito, use \$MVAL (optional, use NONE if unneeded)
# $6 => name of array where we store the timestamp of the operation (opt)
# $7 => id field from resource to be used for storing in $3
# $8 => timeout
# $9- > openstack command to be called
#
# In the command you can reference \$AZ (1 or 2), \$no (running number)
# and \$VAL and \$MVAL (from $4 and $5).
#
# NUMBER STATNM RSRCNM OTHRSRC MORERSRC STIME IDNM COMMAND
createResources()
{
  local ctr no
  declare -i ctr=0
  local QUANT=$1; local STATNM=$2; local RNM=$3
  local ORNM=$4; local MRNM=$5
  local STIME=$6; local IDNM=$7
  shift; shift; shift; shift; shift; shift; shift
  local TIMEOUT=$1; shift
  #if test $TIMEOUTFACT -gt 1; then let TIMEOUT+=2; fi
  eval local LIST=( \"\${${ORNM}S[@]}\" )
  eval local MLIST=( \"\${${MRNM}S[@]}\" )
  if test "$RNM" != "NONE"; then echo -n "New $RNM: "; fi
  local RC=0
  local TIRESP
  FAILEDNO=-1
  for no in `seq 0 $(($QUANT-1))`; do
    local AZN=$(($no%$NOAZS))
    local VAZN=$(($no%$NOVAZS))
    local AZ=$(($AZ+1))
    local VAZ=$(($VAZ+1))
    local VAL=${LIST[$ctr]}
    local MVAL=${MLIST[$ctr]}
    local CMD=`eval echo $@ 2>&1`
    local STM=$(date +%s)
    if test -n "$STIME"; then eval "${STIME}+=( $STM )"; fi
    let APICALLS+=1
    TIRESP=$(ostackcmd_id $IDNM $TIMEOUT $CMD)
    RC=$?
    #echo "DEBUG: ostackcmd_id $CMD => $RC" 1>&2
    updAPIerr $RC
    local TM
    read TM ID STATE <<<"$TIRESP"
    if test $RC == 0; then eval ${STATNM}+="($TM)"; fi
    let ctr+=1
    state2col "$STATE"
    # Workaround for teuto.net
    if test "$1" = "cinder" && [[ $OS_AUTH_URL == *teutostack* ]]; then echo -en " ${RED}+5s${NORM} " 1>&2; sleep 5; fi
    if test $RC != 0; then echo -e "${YELLOW}ERROR: $RNM creation failed$NORM" 1>&2; FAILEDNO=$no; return 1; fi
    if test -n "$ID" -a "$RNM" != "NONE"; then echo -en "$ID $SCOL$STATE$NORM "; fi
    eval ${RNM}S+="($ID)"
    # Workaround for loadbalancer member create
    if test "$STATE" = "PENDING_CREATE"; then sleep 1; fi
  done
  if test "$RNM" != "NONE"; then echo; fi
}
```

### createResourcesCond()
* Lines in Code: [L1254-L1318](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1254-L1318)  
* Purpose: similar to the `createResources()` function, but with an additional condition check before creating each resource
* Description:
  - parameters:
    - same parameters like `createResources()`
    - `$9` condition variable that must be non-empty and not `"0"` for the resource creation to proceed
    - `$10-` OpenStack command to be called
  - initializes various variables and arrays similar to `createResources()`
  - loops through the specified quantity of resources, executing the provided OpenStack command for each resource
  - before executing the command, it evaluates the condition variable ($CONDVAR) to ensure it's non-empty and not `"0"`. otherwise it skips the creation of that resource and continues to the next one.
  - updates the status of the resource creation process based on the command's response
  - handles any errors encountered during the creation process and returns an appropriate exit code.
* Code:
```
# Create a number of resources and keep track of them
# $1 => quantity of resources
# $2 => name of timing statistics array
# $3 => name of resource list array ("S" appended)
# $4 => name of resource array ("S" appended, use \$VAL to ref) (optional)
# $5 => dito, use \$MVAL (optional, use NONE if unneeded)
# $6 => name of array where we store the timestamp of the operation (opt)
# $7 => id field from resource to be used for storing in $3
# $8 => timeout
# $9 => condition variable must be non-empty and not "0"
# $10- > openstack command to be called
#
# In the command you can reference \$AZ (1 or 2), \$no (running number)
# and \$VAL and \$MVAL (from $4 and $5).
#
# NUMBER STATNM RSRCNM OTHRSRC MORERSRC STIME IDNM COMMAND
createResourcesCond()
{
  local ctr no
  declare -i ctr=0
  local QUANT=$1; local STATNM=$2; local RNM=$3
  local ORNM=$4; local MRNM=$5
  local STIME=$6; local IDNM=$7
  shift; shift; shift; shift; shift; shift; shift
  local TIMEOUT=$1; shift
  local CONDVAR=$1; shift
  #if test $TIMEOUTFACT -gt 1; then let TIMEOUT+=2; fi
  eval local LIST=( \"\${${ORNM}S[@]}\" )
  eval local MLIST=( \"\${${MRNM}S[@]}\" )
  if test "$RNM" != "NONE"; then echo -n "New $RNM: "; fi
  local RC=0
  local TIRESP
  FAILEDNO=-1
  for no in `seq 0 $(($QUANT-1))`; do
    local AZN=$(($no%$NOAZS))
    local VAZN=$(($no%$NOVAZS))
    local AZ=$(($AZ+1))
    local VAZ=$(($VAZ+1))
    local VAL=${LIST[$ctr]}
    local MVAL=${MLIST[$ctr]}
    local CMD=`eval echo $@ 2>&1`
    local COND=`eval echo $CONDVAR 2>&1`
    local STM=$(date +%s)
    if test -z "$COND" -o "$COND" == "0"; then echo -n " - "; continue; fi
    if test -n "$STIME"; then eval "${STIME}+=( $STM )"; fi
    let APICALLS+=1
    TIRESP=$(ostackcmd_id $IDNM $TIMEOUT $CMD)
    RC=$?
    #echo "DEBUG: ostackcmd_id $CMD => $RC" 1>&2
    updAPIerr $RC
    local TM
    read TM ID STATE <<<"$TIRESP"
    if test $RC == 0; then eval ${STATNM}+="($TM)"; fi
    let ctr+=1
    state2col "$STATE"
    # Workaround for teuto.net
    if test "$1" = "cinder" && [[ $OS_AUTH_URL == *teutostack* ]]; then echo -en " ${RED}+5s${NORM} " 1>&2; sleep 5; fi
    if test $RC != 0; then echo -e "${YELLOW}ERROR: $RNM creation failed$NORM" 1>&2; FAILEDNO=$no; return 1; fi
    if test -n "$ID" -a "$RNM" != "NONE"; then echo -en "$ID $SCOL$STATE$NORM "; fi
    eval ${RNM}S+="($ID)"
    # Workaround for loadbalancer member create
    if test "$STATE" = "PENDING_CREATE"; then sleep 1; fi
  done
  if test "$RNM" != "NONE"; then echo; fi
}
```

### deleteResources()

* Lines in Code: [L1320-L1390](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1320-L1390) 
* Purpose: provide a function to execute OpenStack commands and handle their responses with helper functions to manage timing statistics, handle errors, and update resource lists.
* Description:
  - parameters:
    - `$1` Name of timing statistics array
    - `$2` Name of the array containing resources (`"S"` appended)
    - `$3` Name of the array to store timestamps for deletion (optional, use `""` if unneeded)
    - `$4` Timeout for the deletion operation
    - `$5-` OpenStack command to be called for resource deletion. The UUID from the resource list is appended to the command.
  - initializes various local variables and arrays based on the provided parameters
  - iterates through the resource list array `${RNM}S` and deletes each resource executing the specified OpenStack command with the resource UUID appended
  - tracks the deletion status and timestamps of each deletion operation
  - If an error occurs during deletion, it retries the deletion operation and continues. It keeps track of the failed deletions and stores them for later re-cleanup.
  - After completing the deletion process, it updates the resource list array `${RNM}S` to reflect any remaining resources
  - returns the number of errors encountered during the deletion process
* Dependencies: responses depend on the `ostackcmd_id()` function
* Code:
```
# Delete a number of resources
# $1 => name of timing statistics array
# $2 => name of array containing resources ("S" appended)
# $3 => name of array to store timestamps (optional, use "" if unneeded)
# $4 => timeout
# $5- > openstack command to be called
# The UUID from the resource list ($2) is appended to the command.
#
# The resource array ($2) will be modified and the delete items (all) be removed from it
#
# STATNM RSRCNM DTIME COMMAND
deleteResources()
{
  local STATNM=$1; local RNM=$2; local DTIME=$3
  local ERR=0
  shift; shift; shift
  local TIMEOUT=$1; shift
  #if test $TIMEOUTFACT -gt 1; then let TIMEOUT+=2; fi
  local FAILDEL=()
  eval local LIST=( \"\${${ORNM}S[@]}\" )
  #eval local varAlias=( \"\${myvar${varname}[@]}\" )
  eval local LIST=( \"\${${RNM}S[@]}\" )
  #echo $LIST
  test -n "$LIST" && echo -n "Del $RNM: "
  #for rsrc in $LIST; do
  local LN=${#LIST[@]}
  local TIRESP
  local IGNERRS=0
  eval "REM${RNM}S=()"
  while test ${#LIST[*]} -gt 0; do
    local rsrc=${LIST[-1]}
    echo -n "$rsrc "
    local DTM=$(date +%s)
    if test -n "$DTIME"; then eval "${DTIME}+=( $DTM )"; fi
    local TM
    let APICALLS+=1
    TIRESP=$(ostackcmd_id id $TIMEOUT $@ $rsrc)
    local RC="$?"
    if test -z "$IGNORE_ERRORS"; then
      updAPIerr $RC
    else
      let IGNERRS+=$RC
      RC=0
    fi
    read TM ID STATE <<<"$TIRESP"
    if test $RC != 0; then
      echo -e "${YELLOW}ERROR deleting $RNM $rsrc; retry and continue ...$NORM" 1>&2
      let ERR+=1
      sleep 5
      TIRESP=$(ostackcmd_id id $(($TIMEOUT+8)) $@ $rsrc)
      RC=$?
      updAPIerr $RC
      if test $RC != 0; then FAILDEL+=($rsrc); fi
    else
      eval ${STATNM}+="($TM)"
    fi
    unset LIST[-1]
    if test "$STATE" = "PENDING_DELETE"; then sleep 1; fi
  done
  if test -n "$IGNORE_ERRORS" -a $IGNERRS -gt 0; then echo -n " ($IGNERRS errors ignored) "; fi
  test $LN -gt 0 && echo
  # FIXME: Should we try again immediately?
  if test -n "$FAILDEL"; then
    echo "Store failed dels in REM${RNM}S for later re-cleanup: ${FAILDEL[*]}"
    eval "REM${RNM}S=(${FAILDEL[*]})"
  fi
  # FIXME: We could try to look for a delete suffix in the command before doing this ...
  # FIXME: This will always be empty ...
  eval "${RNM}S=(${LIST[*]})"
  return $ERR
}
``` 


### waitResources()

* Lines in Code: [L1414-L1482](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1414-L1482) 
* Purpose: ensure that certain resources are in a specific state before proceeding with further actions in automation scripts
* Description:
  - parameters:
    - `$1` Name of the timing statistics array.
    - `$2` Name of the array containing resources (with "S" appended).
    - `$3` Name of the array to collect completion timing stats.
    - `$4` Name of the array with start times.
    - `$5` Value to wait for.
    - `$6` Alternative value to wait for.
    - `$7` Field name to monitor.
    - `$8` Timeout.
    - `$9-` OpenStack command for querying status. The values from $2 get appended to the command.
  - initializes necessary variables and iterates through the resources and queries their status using the provided OpenStack command while collecting timing statistics and logs
  - if the status matches the desired value, it proceeds to the next resource
  - if there's an error or the status doesn't match, it logs an error message and continues waiting
  - repeats this process until the desired state for all resources or the timeout is reached
  - Output:
    - returns the number of resources that did not reach the desired state within the timeout period

* Code:
```
# Wait for resources reaching a desired state
# $1 => name of timing statistics array
# $2 => name of array containing resources ("S" appended)
# $3 => name of array to collect completion timing stats
# $4 => name of array with start times
# $5 => value to wait for
# $6 => alternative value to wait for
# $7 => field name to monitor
# $8 => timeout
# $9- > openstack command for querying status
# The values from $2 get appended to the command
#
# STATNM RSRCNM CSTAT STIME PROG1 PROG2 FIELD COMMAND
waitResources()
{
  ERRRSC=()
  local STATNM=$1; local RNM=$2; local CSTAT=$3; local STIME=$4
  local COMP1=$5; local COMP2=$6; local IDNM=$7
  shift; shift; shift; shift; shift; shift; shift
  local TIMEOUT=$1; shift
  #if test $TIMEOUTFACT -gt 1; then let TIMEOUT+=2; fi
  local STATI=()
  eval local RLIST=( \"\${${RNM}S[@]}\" )
  eval local SLIST=( \"\${${STIME}[@]}\" )
  local LAST=$(( ${#RLIST[@]} - 1 ))
  declare -i ctr=0
  declare -i WERR=0
  local TIRESP
  while test -n "${SLIST[*]}" -a $ctr -le 320; do
    local STATSTR=""
    for i in $(seq 0 $LAST ); do
      local rsrc=${RLIST[$i]}
      if test -z "${SLIST[$i]}"; then STATSTR+=$(colstat "${STATI[$i]}" "$COMP1" "$COMP2"); continue; fi
      local CMD=`eval echo $@ $rsrc 2>&1`
      let APICALLS+=1
      TIRESP=$(ostackcmd_id $IDNM $TIMEOUT $CMD)
      local RC=$?
      updAPIerr $RC
      local TM STAT
      read TM STAT STATE <<<"$TIRESP"
      eval ${STATNM}+="( $TM )"
      if test $RC != 0; then echo -e "\n${YELLOW}ERROR: Querying $RNM $rsrc failed$NORM" 1>&2; return 1; fi
      STATI[$i]=$STAT
      STATSTR+=$(colstat "$STAT" "$COMP1" "$COMP2")
      STE=$?
      echo -en "Wait $RNM: $STATSTR\r"
      if test $STE != 0; then
        if test $STE == 1 -o $STE == 3; then
          echo -e "\n${YELLOW}ERROR: $NM $rsrc status $STAT$NORM" 1>&2 #; return 1
          ERRRSC[$WERR]=$rsrc
          let WERR+=1
        fi
        TM=$(date +%s)
        TM=$(math "%i" "$TM-${SLIST[$i]}")
        eval ${CSTAT}+="($TM)"
        if test $STE -ge 2; then GRC=0; else GRC=$STE; fi
        log_grafana "wait$RNM" "$COMP1" "$TM" "$GRC"
        unset SLIST[$i]
      fi
    done
    echo -en "Wait $RNM: $STATSTR\r"
    if test -z "${SLIST[*]}"; then echo; return $WERR; fi
    let ctr+=1
    sleep 2
  done
  if test $ctr -ge 320; then let WERR+=1; fi
  echo
  return $WERR
}
```



### waitlistResources()

* Lines in Code: [L1484-L1595](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1484-L1595) 
* Purpose: provide a versatile and robust tool for waiting for resources to reach a desired state in an OpenStack environment
* Description:
  - parameters:
    - `$1` Name of timing statistics array
    - `$2` Name of array containing resources ("S" appended)
    - `$3` Name of array to collect completion timing stats
    - `$4` Name of array with start times
    - `$5` Value to wait for (special XDELX)
    - `$6` Alternative value to wait for (special: 2ndary XDELX results in waiting also for ERRORED resources)
    - `$7` Number of column (0 based)
    - `$8` Timeout
    - `$9-` OpenStack command for querying status. The values from `$2` get appended to the command.
  - initializes arrays to store resource names, start times, and statuses for managing the waiting process
  - loops through the resources, querying their status using the provided OpenStack command and waiting until their desired state or the timeout is reached
  - handles errors encountered during the waiting process and provides feedback on the progress of the waiting operation, including the number of resources not in the desired state, the time elapsed, and the remaining resources
  - returns the number of resources not in the desired state after the waiting process completes or the timeout is reached

* Code:
```
# Wait for resources reaching a desired state
# $1 => name of timing statistics array
# $2 => name of array containing resources ("S" appended)
# $3 => name of array to collect completion timing stats
# $4 => name of array with start times
# $5 => value to wait for (special XDELX)
# $6 => alternative value to wait for 
#       (special: 2ndary XDELX results in waiting also for ERRORED res.)
# $7 => number of column (0 based)
# $8 => timeout
# $9- > openstack command for querying status
# The values from $2 get appended to the command
#
# Return value: Number of resources not in desired state (e.g. error, wrong state, missing, ...)
#
# STATNM RSRCNM CSTAT STIME PROG1 PROG2 FIELD COMMAND
waitlistResources()
{
  ERRRSC=()
  local STATNM=$1; local RNM=$2; local CSTAT=$3; local STIME=$4
  local COMP1=$5; local COMP2=$6; local COL=$7
  local NERR=0
  shift; shift; shift; shift; shift; shift; shift
  local TIMEOUT=$1; shift
  #echo "waitlistResources $STATNM $RNM $COMP1 $COL $@"
  #if test $TIMEOUTFACT -gt 1; then let TIMEOUT+=2; fi
  local STATI=()
  eval local RLIST=( \"\${${RNM}S[@]}\" )
  eval RRLIST=( \"\${${RNM}S[@]}\" )
  eval local SLIST=( \"\${${STIME}[@]}\" )
  local LAST=$(( ${#RLIST[@]} - 1 ))
  if test ${#RLIST[@]} != ${#SLIST[@]}; then echo " WARN: RLIST \"${RLIST[@]}\" SLIST \"${SLIST[@]}\""; fi
  local PARSE="^|"
  local WAITVAL
  #echo "waitlistResources \"${RLIST[*]}\" \"${SLIST[*]}\"" 1>&2
  if test "$COMP1" == "XDELX"; then WAITVAL="del"; else WAITVAL="$COMP1"; fi
  for no in $(seq 1 $COL); do PARSE="$PARSE[^|]*|"; done
  PARSE="$PARSE *\([^|]*\)|.*\$"
  #echo "$PARSE"
  declare -i ctr=0
  declare -i WERR=0
  declare -i misserr=0
  local waitstart=$(date +%s)
  if test -n "$CSTAT" -a "$CLEANUPMODE" != "1"; then MAXWAIT=240; else MAXWAIT=30; fi
  if test -z "${RLIST[*]}"; then return 0; fi
  while test -n "${RRLIST[*]}" -a $ctr -le $MAXWAIT; do
    local STATSTR=""
    local CMD=`eval echo $@ 2>&1`
    ostackcmd_tm $STATNM $TIMEOUT $CMD
    if test $? != 0; then
      echo -e "\n${YELLOW}ERROR: $CMD => $OSTACKRESP$NORM" 1>&2
      # Only bail out after 6th error;
      # so we retry in case there are spurious 500/503 (throttling) errors
      # Do not give up so early on waiting for deletion ...
      let NERR+=1
      if test $NERR -ge 6 -a "$COMP1" != "XDELX" -o $NERR -ge 24; then return 1; fi
      sleep 5
    fi
    local TM
    #misserr=0
    for i in $(seq 0 $LAST ); do
      local rsrc=${RLIST[$i]}
      if test -z "${SLIST[$i]}"; then STATSTR+=$(colstat "${STATI[$i]}" "$COMP1" "$COMP2"); continue; fi
      local STAT=$(echo "$OSTACKRESP" | grep "^| $rsrc" | sed -e "s@$PARSE@\1@" -e 's/ *$//')
      #echo "STATUS: \"$STAT\""
      if test "$COMP1" == "XDELX" -a -z "$STAT"; then STAT="XDELX"; fi
      STATI[$i]="$STAT"
      STATSTR+=$(colstat "$STAT" "$COMP1" "$COMP2")
      STE=$?
      #echo -en "Wait $RNM $rsrc: $STATSTR\r"
      # Found or ERROR
      if test $STE != 0; then
        # ERROR
        if test $STE == 1 -o $STE == 3; then
          # Really wait for deletion of errored resources?
          if test "$COMP2" == "XDELX"; then continue; fi
          ERRRSC[$WERR]=$rsrc
          let WERR+=1
          let misserr+=1
          echo -e "\n${YELLOW}ERROR: $NM $rsrc status $STAT$NORM" 1>&2 #; return 1
        fi
        # Found
        TM=$(date +%s)
        TM=$(math "%i" "$TM-${SLIST[$i]}")
        unset RRLIST[$i]
        unset SLIST[$i]
        #echo -e "State $STAT reached for ($i) $rsrc in $TM secs, remain \"${SLIST[*]}\"" 1>&2
        if test -n "$CSTAT"; then
          eval ${CSTAT}+="($TM)"
          if test $STE -ge 2; then GRC=0; else GRC=$STE; fi
          log_grafana "wait$RNM" "$COMP1" "$TM" "$GRC"
        fi
      fi
    done
    echo -en "\rWait $WAITVAL $RNM[${#SLIST[*]}/${#RLIST[*]}]: $STATSTR "
    # Save 3s
    if test -z "${SLIST[*]}"; then break; fi
    # We can stop waiting if all resources have failed/disappeared (more than once)
    if test $misserr -ge ${#RLIST[@]} -a $WERR -ge $((${#RLIST[@]}*2)); then break; fi
    sleep 3
    let ctr+=1
  done
  if test $ctr -ge $MAXWAIT; then let WERR+=${#SLIST[*]}; let misserr+=${#SLIST[*]}; fi
  if test -n "${SLIST[*]}"; then
    echo " TIMEOUT $(($(date +%s)-$waitstart))"
    echo -e "\n${YELLOW}Wait TIMEOUT/ERROR $misserr ${NORM} ($(($(date +%s)-$waitstart))s, $ctr iterations), LEFT: ${RED}${RRLIST[*]}:${SLIST[*]}${NORM}" 1>&2
    #FIXME: Shouldn't we send an alarm right here?
  else
    echo " ($(($(date +%s)-$waitstart))s, $ctr iterations)"
  fi
  return $misserr
}
```

### extract_ip()

* Lines in Code: [L2074-L2078](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2074-L2078) 
* Purpose: extracts the IP address from the output of the `neutron port-show` command, which provides detailed information about a Neutron port
* Description:
  - parameters:
    - `$1` the output of the `neutron port-show` command as input
  - uses `grep` to search for lines containing the string `'| fixed_ips '` containing information about the IP addresses associated with the port
  - then `sed` is used with the pattern stored in the variable `$PORTFIXED` to extract and format the IP address from the matched line
  - outputs the extracted IP address


## Main Functions

### MAIN LOOP


* Lines in Code: [L4098-L4504](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4098-L4504) 
* Purpose: main part to orchestrate the deployment, testing, and cleanup of resources in an OpenStack environment, while also monitoring for errors and performance issues
* Description:
  - Entering the loop: the first section sets up the environment, initializes error counters, and declares arrays to manage resources and track deployment progress. It enters the while loop that continues as long as the loop counter `loop` is not equal to `MAXITER` (maximum iteration count), `INTERRUPTED` is unset and the loop will continue as long as the stop signal file `stop-os-hm` does not exist (`! -e stop-os-hm`).
  - First the Error Counters are declared as integer variables, including `PINGERRORS`, `APIERRORS`, `APITIMEOUTS`, `VMERRORS`, `LBERRORS`, `WAITERRORS` and `CONNERRORS`. These counters track different types of errors that may occur during the deployment process
  - Next arrays are declared to store the start times of resource creation operations. They store timestamps for various resources being created during the deployment process, such as volumes, VMs, LBs, etc.
  - Followed by the declaration of the arrays to manage resources across different OpenStack services, such as `Neutron` (networking), `Cinder` (block storage) and `Nova` (compute), meaning there are arrays to keep track of resources created during the deployment process and to perform cleanup operations later: 
    - `NETS` (network IDs), 
    - `SUBNETS` (subnet IDs), 
    - `SGROUPS` (security group IDs), 
    - `PORTS` (port IDs), 
    - `VIPS` (VIP IDs), 
    - `FIPS` (floating IPs), 
    - `VOLUMES` (volume IDs), 
    - `VMS` (VM IDs), 
    - `LBAASS` (load balancer IDs), 
    - etc.
  - After that the Alarm Buffer and Alarm Counters are declared:
    - `ALARMBUFFER` array to buffer alarm messages before sending them
    - `SENTALARMS` and `BUFFEREDALARMS` are integer variables to count the sent and buffered alarms
  - Then starts the Main Functionality by initializing `MSTART` (start time) with the urrent timestamp
  - Followed by checking for the `OPENSTACKTOKEN` retrieving the token with `getToken()` and stting the token timestamp `TOKENSTAMP` with the current timestamp.
  - the main functionality  has several conditional branches based on the first argument `$1` passed to the script:
    - if `$1` is "CLEANUP", the cleanup process is triggered involving deleting various resources
    - if `$1` is "CONNTEST", connectivity testing is initiated
    -  Otherwise the deployment process is proceeded
  - the deployment process starts by checking if a new project needs to be created based on the value of `REFRESHPRJ`.
    - retrieves image IDs, flavor information, and other necessary details for deployment.
    - creates routers, networks, subnets, router interfaces, security groups, load balancers, volumes, key pairs, ports, and JumpHost volumes.
    - waits for the completion of the resource creations using wait functions (see below*)
    - creates VMs and FIPs for both JumpHosts and regular VMs
    - performs connectivity tests between VMs, tests load balancers if enabled, and performs additional tests if specified (e.g., full connection tests)
    - cleans up resources if required, deletes routers, networks, subnets, security groups, load balancers, VMs, FIPs, volumes, key pairs, and ports.
    - raises alarms for slow performance and sends recovery alarms
    - logs and reports cumulative errors, timeouts, retries, and other statistics at the end of each run
  - * wait functions: ensuring that the deployment process waits until resources are ready before proceeding further. They help handle asynchronous operations in the OpenStack environment and ensure that subsequent steps in the deployment process are executed only when the required resources are available in the desired state.
    - `waitLBs` waits for the load balancers specified in the array `$LBAASS` to reach the provisioning status`"ACTIVE"`. Therefore it calls `waitlistResources()` with the parameters `LBAAS` and `"ACTIVE"`. If the `--nostat` flag is not provided, it also waits for LB statistics `LBCSTATS` to be available. Any errors are handled by calling `handleWaitErr()`, which checks for errors in the LB status and prints them if necessary.
    - `waitdelLBs` waits for LBs from the array `${DELLBAASS[*]}` to be deleted. Therefore calls `waitlistResources()` with the parameters `LBSTATS` and `"XDELX"` indicating deletion. The deletion is retried, if it did not succeed.
    - `waitlistResources()` is a general-purpose function, described above used for waiting for resources to reach a certain state. in this section it takes the array containing resource IDs `$LBSTATS` or `$LBCSTATS` as parameters and the type of resource `$LBAAS`, the expected status `"ACTIVE"` and the timeout value. It repeatedly queries the OpenStack API to check the status of the specified resources until they reach the expected state or the timeout is reached. With the `--nostat` flag unset, it also waits for additional resource statistics.

* Code:
```
# MAIN LOOP
while test $loop != $MAXITER -a -z "$INTERRUPTED" -a ! -e stop-os-hm; do

declare -i PINGERRORS=0
declare -i APIERRORS=0
declare -i APITIMEOUTS=0
declare -i VMERRORS=0
declare -i LBERRORS=0
declare -i WAITERRORS=0
declare -i CONNERRORS=0
declare -i APICALLS=0
declare -i ROUNDVMS=0

# Arrays to store resource creation start times
declare -a VOLSTIME=()
declare -a JVOLSTIME=()
declare -a VMSTIME=()
declare -a JVMSTIME=()
declare -a LBSTIME=()
declare -a LBDTIME=()

# List of resources - neutron
declare -a NETS=()
declare -a SUBNETS=()
declare -a JHNETS=()
declare -a JHSUBNETS=()
declare -a SGROUPS=()
declare -a JHPORTS=()
declare -a PORTS=()
declare -a VIPS=()
declare -a FIPS=()
declare -a FLOATS=()
# cinder
declare -a JHVOLUMES=()
declare -a VOLUMES=()
# nova
declare -a KEYPAIRS=()
declare -a VMS=()
declare -a JHVMS=()
# LB
declare -a LBAASS=()
declare -a DELLBAASS=()
declare -a POOLS=()
declare -a LISTENERS=()
declare -a MEMBERS=()
declare -a HEALTHMONS=()
SNATROUTE=""

declare -a ALARMBUFFER=()
declare -i SENTALARMS=0
declare -i BUFFEREDALARMS=0

# Main
MSTART=$(date +%s)
# Get token
if test -n "$OPENSTACKTOKEN"; then
  getToken
  if test -z "$CINDER_EP" -o -z "$NOVA_EP" -o -z "$GLANCE_EP" -o -z "$NEUTRON_EP" -o -z "$TOKEN"; then
    echo "Trouble getting token/catalog, retry ..."
    sleep 2
    getToken
  fi
  TOKENSTAMP=$(date +%s)
fi
# Debugging: Start with volume step
if test "$1" = "CLEANUP"; then
  CLEANUPMODE=1
  if test -n "$2"; then RPRE=$2; if test ${RPRE%_} == ${RPRE}; then RPRE=${RPRE}_; fi; fi
  if test "$TAG" == "1"; then TAGARG="--tag ${RPRE%_}"; fi
  echo -e "$BOLD *** Start cleanup $RPRE $TAGARG *** $NORM"
  #SECONDNET=1
  cleanup
  echo -e "$BOLD *** Cleanup complete *** $NORM"
  # We always return 0 here, as we dont want to stop the testing on failed cleanups.
  exit 0
elif test "$1" = "CONNTEST"; then
  if test -n "$2"; then RPRE=$2; if test ${RPRE%_} == ${RPRE}; then RPRE=${RPRE}_; fi; fi
  if test "$TAG" == "1"; then TAGARG="--tag ${RPRE%_}"; fi
  while test $loop != $MAXITER -a -z "$INTERRUPTED"; do
   echo -e "$BOLD *** Start connectivity test for $RPRE ($((loop+1))/$MAXITER) *** $NORM"
   # Only collect resource on e. 10th iteration
   if test "$(($loop%10))" == 0; then collectRes; else echo " Reuse known resources ..."; sleep 2; fi
   if test -z "${VMS[*]}"; then echo "No VMs found"; exit 1; fi
   #echo "FLOATs: ${FLOATS[*]} JHVMS: ${JHVMS[*]}"
   testjhinet
   RC=$?
   if test $RC != 0; then
     sendalarm 2 "JH unreachable" "$ERR" 20
     if test -n "$EXITERR"; then exit 2; fi
     let VMERRORS+=$RC
     errwait $ERRWAIT
   fi
   #echo "REDIRS: ${REDIRS[*]}"
   wait222
   # Defer alarms
   #if test $? != 0; then exit 2; fi
   testsnat
   RC=$?
   if test $RC != 0; then
     sendalarm 2 "VMs unreachable/can not ping outside" "$ERR" 16
     if test -n "$EXITERR"; then exit 3; fi
     let VMERRORS+=$RC
     errwait $ERRWAIT
   fi
   if test -n "$RESHUFFLE" -a -n "$STARTRESHUFFLE"; then reShuffle; fi
   fullconntest
   #if test $? != 0; then exit 4; fi
   log_grafana ping stats $FPRETRY $FPERR
   if test $FPERR -gt 0; then
     PINGERRORS+=$FPERR
     sendalarm 2 "Connectivity errors" "$FPERR + $FPRETRY\n$ERR" 5
     if test -n "$EXITERR"; then exit 4; fi
     # Error counting done by fullconntest already
     errwait $ERRWAIT
   elif test $FPRETRY != 0; then
     echo -e "${YELLOW}Warning:${NORM} Needed $FPRETRY ping retries"
   fi
   log_grafana ping errors 1 $FPERR
   log_grafana ping retries 1 $FPRETRY
   if test -n "$RESHUFFLE"; then
     reShuffle
     fullconntest
     log_grafana ping stats $FPRETRY $FPERR
     if test $FPERR -gt 0; then
       PINGERRORS+=$FPERR
       sendalarm 2 "Connectivity errors" "$FPERR + $FPRETRY\n$ERR" 5
       if test -n "$EXITERR"; then exit 4; fi
       # Error counting done by fullconntest already
       errwait $ERRWAIT
       fi
     let SUCCRUNS+=1
   fi
   echo -e "$BOLD *** Connectivity test complete *** $NORM"
   let SUCCRUNS+=1
   if test $SUCCWAIT -ge 0; then sleep $SUCCWAIT; else echo -n "Hit enter to continue ..."; read ANS; fi
   let loop+=1
   # Refresh token after 10hrs
   if test -n "$TOKENSTAMP" && test $(($(date +%s)-$TOKENSTAMP)) -ge 36000; then
     getToken
     TOKENSTAMP=$(date +%s)
   fi
   # TODO: We don't do anything with the collected statistics in CONNTEST yet ... fix!
  done
  exit 0 #$RC
else # test "$1" = "DEPLOY"; then
 if test "$REFRESHPRJ" != 0 && test $(($RUNS%$REFRESHPRJ)) == 0; then createnewprj; fi
 # Complete setup
 echo -e "$BOLD *** Start deployment $((loop+1))/$MAXITER for $NOAZS SNAT JumpHosts + $NOVMS VMs *** $NORM ($TRIPLE) $TAGARG"
 date
 unset THISRUNSUCCESS
 # Image IDs
 JHIMGID=$(ostackcmd_search "$JHIMG" $GLANCETIMEOUT glance image-list $JHIMGFILT | awk '{ print $2; }')
 if test -z "$JHIMGID" -o "$JHIMGID" == "0"; then sendalarm 1 "No JH image $JHIMG found, aborting." "" $GLANCETIMEOUT; exit 1; fi
 IMGID=$(ostackcmd_search "$IMG" $GLANCETIMEOUT glance image-list $IMGFILT | awk '{ print $2; }')
 if test -z "$IMGID" -o "$IMG" == "0"; then sendalarm 1 "No image $IMG found, aborting." "" $GLANCETIMEOUT; exit 1; fi
 let APICALLS+=2
 # Retrieve root volume size
 ostackcmd_tm_retry GLANCESTATS $GLANCETIMEOUT glance image-show -f json $JHIMGID
 if test $? != 0; then
  let APIERRORS+=1; sendalarm 1 "glance image-show failed" "" $GLANCETIMEOUT
  errwait $ERRWAIT
  let loop+=1
  continue
 else
  MD=$(echo "$OSTACKRESP" | jq '.min_disk' | tr -d '"')
  SZ=$(echo "$OSTACKRESP" | jq '.size' | tr -d '"')
  USER=$(echo "$OSTACKRESP" | jq '.properties.image_original_user' | tr -d '"')
  SZ=$((SZ/1024/1024/1024))
  if test "$SZ" -gt "$MD"; then MD=$SZ; fi
  JHVOLSIZE=$(($MD+$ADDJHVOLSIZE))
  if test -n "$USER" -a "$USER" != "null"; then JHDEFLTUSER="$USER"; fi
 fi
 ostackcmd_tm_retry GLANCESTATS $GLANCETIMEOUT glance image-show -f json $IMGID
 if test $? != 0; then
  let APIERRORS+=1; sendalarm 1 "glance image-show failed" "" $GLANCETIMEOUT
 else
  MD=$(echo "$OSTACKRESP" | jq '.min_disk' | tr -d '"')
  SZ=$(echo "$OSTACKRESP" | jq '.size' | tr -d '"')
  USER=$(echo "$OSTACKRESP" | jq '.properties.image_original_user' | tr -d '"')
  SZ=$((SZ/1024/1024/1024))
  if test "$SZ" -gt "$MD"; then MD=$SZ; fi
  VOLSIZE=$(($MD+$ADDVMVOLSIZE))
  if test -n "$USER" -a "$USER" != "null"; then DEFLTUSER="$USER"; fi
 fi
 #let APICALLS+=2
 # Check VM flavor
 ostackcmd_tm_retry NOVASTATS $NOVATIMEOUT nova flavor-show -f json $FLAVOR
 if test $? != 0; then
  let APIERRORS+=1; sendalarm 1 "nova flavor-show $FLAVOR failed" "" $NOVATIMEOUT; exit 1
 else
  VMFLVDISK=$(echo "$OSTACKRESP" | jq '.disk')
  if test $VMFLVDISK -lt $VOLSIZE -a -n "$BOOTFROMIMAGE"; then
    patch_openstackclient
    NEED_BLKDEV=1
    VMVOLSIZE=${VMVOLSIZE:-$VOLSIZE}
  else
    unset NEED_BLKDEV
    #unset VMVOLSIZE
  fi
 fi
 echo "Using images JH $JHDEFLTUSER@$JHIMG ($JHVOLSIZE GB), VM $DEFLTUSER@$IMG ($VOLSIZE GB)"
 echo "Deploying on AZs ${AZS[*]} (Volumes: ${VAZS[*]}, Networks: ${NAZS[*]})"
 if createRouters; then
  if createNets; then
   if createSubNets; then
    if createRIfaces; then
     if createSGroups -a -z "$INTERRUPTED" -a ! -e stop-os-hm; then
      createLBs;
      if createJHVols; then
       if createVIPs; then
        if createJHPorts; then
         if createVols; then
          if createKeypairs; then
           createPorts
           waitJHVols # TODO: Error handling
           if createJHVMs; then
            let ROUNDVMS=$NOAZS
            if createFIPs; then
             waitVols  # TODO: Error handling
             if createVMs; then
              let ROUNDVMS+=$NOVMS
              waitJHVMs
              RC=$?
              if test $RC != 0; then
               #sendalarm $RC "Timeout waiting for JHVM ${RRLIST[*]}" "$WAITERRSTR" $((4*$MAXWAIT))
               # FIXME: Shouldn't we count errors and abort here? Without JumpHosts, the rest is hopeless ...
               if test $RC -gt $NOAZS; then let VMERRORS+=$NOAZS; else let VMERRORS+=$RC; fi
              else
               # loadbalancer
               waitLBs
               LBWAITERR=$?
               if test -n "$LBAASS"; then LBERRORS=$LBWAITERR; fi
               # No error handling here (but alarms are generated)
               waitVMs
               # Errors will be counted later again
               setmetaVMs
               create2ndSubNets
               create2ndPorts
               # Test JumpHosts
               # NOTE: Alarms and Grafana error logging are not fully aligned here
               testjhinet
               RC=$?
               # Retry
               if test $RC != 0; then echo "$ERR"; sleep 5; testjhinet; RC=$?; fi
               # Non-working JH breaks us ...
               if test $RC != 0; then
                 let VMERRORS+=$RC
                 sendalarm $RC "$ERR" "" 70
                 errwait $VMERRWAIT
                 # FIXME: Shouldn't we abort here?
                 echo -e "${BOLD}Aborting this deployment due to non-functional JH, clean up now ...${NORM}"
                 sleep 1
                 MSTOP=$(date +%s)
               else
                # Test normal hosts
                #setPortForward
                setPortForwardGen
                WSTART=$(date +%s)
                wait222
                WAITERRORS=$?
                # No need to send alarm yet, will do after testsnat
                #if test $WAITERRORS != 0; then
                #  sendalarm $RC "$ERR" "" $((4*$MAXWAIT))
                #  errwait $VMERRWAIT
                #fi
                testsnat
                RC=$?
                let VMERRORS+=$((RC/2))
                if test $RC != 0; then
                  sendalarm $RC "$ERR" "" $((4*$MAXWAIT))
                  errwait $VMERRWAIT
                fi
                # Attach and config 2ndary NICs
                config2ndNIC
                MSTOP=$(date +%s)
                # Full connection test
                if test -n "$FULLCONN" -a -z "$INTERRUPTED" -a ! -e stop-os-hm; then
                  fullconntest
                  # Test for FPERR instead?
                  if test $FPERR -gt 0; then
                    PINGERRORS+=$FPERR
                    sendalarm 2 "Connectivity errors" "$FPERR + $FPRETRY\n$ERR" 5
                    errwait $ERRWAIT
                  elif test $FPRETRY != 0; then
                   echo -e "${YELLOW}Warning:${NORM} Needed $FPRETRY ping retries"
                  fi
                  log_grafana ping stats $FPRETRY $FPERR
                  if test -n "$SECONDNET" -a -n "$RESHUFFLE"; then
                    reShuffle
                    fullconntest
                    if test $FPERR -gt 0; then
                      PINGERRORS+=$FPERR
                      log_grafana ping stats $FPRETRY $FPERR
                      sendalarm 2 "Connectivity errors" "$FPERR + $FPRETRY\n$ERR" 5
                      errwait $ERRWAIT
                    fi
                  fi
		  if test -n "$IPERF"; then iperf3test; fi
                  #MSTOP=$(date +%s)
                fi
                # TODO: Create disk ... and attach to JH VMs ... and test access
                # TODO: Attach additional net interfaces to JHs ... and test IP addr
                WAITTIME+=($(($MSTOP-$WSTART)))
                # Test load balancer
                if test -n "$LOADBALANCER" -a $LBERRORS = 0 -a -z "$INTERRUPTED" -a ! -e stop-os-hm; then
		 LBACTIVE=1
		 testLBs
                else
		 LBACTIVE=0
		fi
                TESTTIME=$(($(date +%s)-$MSTOP))
                echo -e "$BOLD *** SETUP DONE ($(($MSTOP-$MSTART))s), TESTS DONE (${TESTTIME}s), DELETE AGAIN $NORM"
                let SUCCRUNS+=1
                THISRUNSUCCESS=1
		sleep 1
		if test $SUCCWAIT -ge 0; then echo -n "Sleep ... (safe to hit ^C) ..."; sleep $SUCCWAIT; echo;
		else echo -n "Hit enter to continue ..."; read ANS; fi
                # Refresh token if needed
                if test -n "$TOKENSTAMP" && test $(($(date +%s)-$TOKENSTAMP)) -ge 36000; then
                  getToken
                  TOKENSTAMP=$(date +%s)
                fi
                # Subtract waiting time (5s here)
                MSTART=$(($MSTART+$(date +%s)-$MSTOP))
                if test -n "$LOADBALANCER" -a "$LBACTIVE" = "1"; then cleanLBs; fi
               fi
               # TODO: Detach and delete disks again
              fi; #JH wait successful
             fi; deleteVMs
            fi; deleteFIPs
           fi; deleteJHVMs
          fi; deleteKeypairs
         fi; waitdelVMs; deleteVols
        fi; waitdelJHVMs
        #echo -e "${BOLD}Ignore port del errors; VM cleanup took care already.${NORM}"
        IGNORE_ERRORS=1
        delete2ndPorts
        #if test -n "$SECONDNET" -o -n "$MANUALPORTSETUP"; then deletePorts; fi
        #deletePorts; deleteJHPorts	# not strictly needed, ports are del by VM del
        unset IGNORE_ERRORS
       fi; deleteVIPs
      fi; waitLBs --nostat; deleteLBs
      delPortsLBs
      deleteJHVols
     # There is a chance that some VMs were not created, but ports were allocated, so clean ...
     fi; cleanupPorts; deleteSGroups
    fi # Wait for LBs to vanish, try deleting again, in case they had been in PENDING_XXXX before
    CLEANUPMODE=1
    if ! waitdelLBs; then unset CLEANUPMODE LBDSTATS; LBAASS=(${DELLBAASS[*]}); deleteLBs; waitdelLBs; fi
    unset CLEANUPMODE; deleteRIfaces
   fi; deleteSubNets
  fi; deleteNets
 fi
 # We may recycle the router
 if test $(($loop+1)) == $MAXITER -o -n "$INTERRUPTED" -o $((($loop+1)%$ROUTERITER)) == 0 -o -e stop-os-hm; then deleteRouters; fi
 #echo "${NETSTATS[*]}"
 echo -e "$BOLD *** Cleanup complete *** $NORM"
 THISRUNTIME=$(($(date +%s)-$MSTART+$TESTTIME))
 # Only account successful runs for total runtime stats
 if test -n "$THISRUNSUCCESS"; then
   TOTTIME+=($THISRUNTIME)
 fi
 # Raise an alarm if we have not yet sent one and we're very slow despite this
 if test -n "$OPENSTACKTOKEN"; then
   if test -n "$BOOTALLATONCE"; then CON=400; NFACT=12; FACT=24; else CON=384; NFACT=12; FACT=36; fi
 else
   if test -n "$BOOTALLATONCE"; then CON=416; NFACT=16; FACT=24; else CON=400; NFACT=16; FACT=36; fi
 fi
 if test "$VOLNEEDSTAG" == "1"; then let FACT+=2; fi
 MAXCYC=$(($CON+($FACT+$NFACT/2)*$NOAZS+$NFACT*$NONETS+$FACT*$NOVMS))
 MINCYC=$(($MAXCYC/6))
 if test -n "$SECONDNET"; then let MAXCYC+=$(($NFACT*$NONETS+$NFACT*$NOVMS)); fi
 if test -n "$RESHUFFLE"; then let MAXCYC+=$((2*$NFACT*$NOVMS)); fi
 if test -n "$FULLCONN"; then let MAXCYC+=$(($NOVMS*$NOVMS/10)); fi
 if test -n "$IPERF"; then let MAXCYC+=$((6*$NONETS)); fi
 if test -n "$LOADBALANCER"; then let MAXCYC+=$((36+4*$NOVMS+$WAITLB)); fi
 if test -n "$SKIPKILLLB"; then let MAXCYC-=$((20+2*$NOVMS)); fi
 # FIXME: We could check THISRUNSUCCESS instead?
 SLOW=0
 if test $VMERRORS = 0 -a $WAITERRORS = 0 -a $THISRUNTIME -gt $MAXCYC; then
    sendalarm 1 "SLOW PERFORMANCE" "Cycle time: $THISRUNTIME (max $MAXCYC)" $MAXCYC
    #waiterr $WAITERR
    SLOW=1
 fi
 if test -z "$THISRUNSUCCESS"; then let SLOW+=1; fi
 RELPERF=$(echo "scale=2; 10*$THISRUNTIME/$MAXCYC" | bc -l)
 log_grafana "totDur" "$MAXCYC" "$RELPERF" "$SLOW"
 sendbufferedalarms
 sendrecoveryalarm
 allstats
 if test -n "$FULLCONN"; then CONNTXT="$CONNERRORS Conn Errors, "; else CONNTXT=""; fi
 if test -n "$LOADBALANCER"; then LBTXT="$LBERRORS LB Errors, "; else LBTXT=""; fi
 echo -e "This run ($((loop+1))/$MAXITER): Overall $ROUNDVMS / ($NOVMS + $NOAZS) VMs, $APICALLS CLI calls: $(($(date +%s)-$MSTART))s+${TESTTIME}s=${THISRUNTIME}s $((100*$THISRUNTIME/$MAXCYC))%\n $VMERRORS VM login errors, $WAITERRORS VM timeouts, $APIERRORS API errors (of which $APITIMEOUTS API timeouts), $PINGERRORS Ping Errors\n ${CONNTXT}${LBTXT}$(date +'%Y-%m-%d %H:%M:%S %Z')"
#else
#  usage
fi
let CUMAPIERRORS+=$APIERRORS
let CUMAPITIMEOUTS+=$APITIMEOUTS
let CUMVMERRORS+=$VMERRORS
let CUMLBERRORS+=$LBERRORS
let CUMPINGRETRIES+=$FPRETRY
let CUMPINGERRORS+=$PINGERRORS
let CUMWAITERRORS+=$WAITERRORS
let CUMCONNERRPRS+=$CONNERRORS
let CUMAPICALLS+=$APICALLS
let CUMVMS+=$ROUNDVMS
let RUNS+=1
```