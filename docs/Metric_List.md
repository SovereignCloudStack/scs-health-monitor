# METRIC OVERVIEW

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

|Command-list	|Lines in Code |Code |Description|
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

	
|Method-list |Lines in Code |Code |Description|
|----------|----------|----------|----------|	
|All ||||
|boot||||
|console-log
|create |[1742 - 1752](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1742-L1752) || orchestrates the creation of networks, handling any errors that may occur during the process and returning an appropriate error code: initializes the `ERC` variable to zero, used to track any errors that occur during the network creation process. Then it calls the `createResources`function to create the single `JHNET`-network `${RPRE}NET_JH` and assigns the output to `ERC`, if successful. If an error occurs, 'ERC' is updated with the error code. Then it checks if the number of availability zones `NONAZS` is less than or equal to one. If `true`, it creates networks for each VM `NONETS` without specifying any availability zones. If `false`, it creates networks for each virtual machine and specifies the availability zone hint based on the array `NAZS`. Then returns the final error code ERC to indicate the success or failure of the network creation process.
||1989 - 1993| `createJHVols(){ JVOLSTIME=()   createResources $NOAZS VOLSTATS JHVOLUME NONE NONE JVOLSTIME id $CINDERTIMEOUT cinder create --image-id $JHIMGID --availability-zone \${VAZS[\$VAZN]} --name ${RPRE}RootVol_JH\$no $JHVOLSIZE }`| responsible for creating Cinder volumes: initializes an array `JVOLSTIME=()` to store timestamps related to the creation of Cinder volumes and calls the `createResources` function with several arguments to create Cinder volumes using the cinder create command: `$NOAZS` (Number of availability zones), `VOLSTATS` (statistics related to volume status), `JHVOLUME` (prefix for the vol name), `NONE` (placeholder), `JVOLSTIME` (array of timestamps) `id` (column to retrieve the vol ID), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder create` command to create the volume specifies the image ID `$JHIMGID`, availability zone, vol name and vol size `$JHVOLSIZE`. The vol name is constructed using the prefix `${RPRE}RootVol_JH` followed by an index `$no`| creates networks for both the Jump Host and VMs in the OpenStack environment, handles any errors and returns exit codes by caslling the `createResources` function to create a network for the JH and specifing the following parameters: `1` (number of networks to create), `NETSTATS` (statistics related to network status), `JHNET` (prefix for the network name), `NONE` (placeholder), `id` (column to retrieve the network ID), `$NETTIMEOUT` (timeout value for the operation), `neutron net-create "${RPRE}NET_JH"`is the actual `neutron` command to create the network for the JH constructing the network name using the prefix `${RPRE}NET_JH`. Then the creation of networks for VM is handled with an if statementthat checks whether there is only one availability zone (NONAZS <= 1) so it would not specify an availability zone hint. Else it specifies an availability zone hint based on the available availability zones. The return `$ERC` statement returns the value that indicates whether any errors occurred during the network creation process|
||2008 - 2013|`createVols() { if test -n "$BOOTFROMIMAGE"; then return 0; fi VOLSTIME=() createResources $NOVMS VOLSTATS VOLUME NONE NONE VOLSTIME id $CINDERTIMEOUT cinder create --image-id $IMGID --availability-zone \${VAZS[\$VAZN]} --name ${RPRE}RootVol_VM\$no $VOLSIZE}`| creates Cinder volumes for virtual machines, except when the virtual machines are booted from an image therefore it checks if the variable `$BOOTFROMIMAGE` is not empty, which would mean the virtual machines should be booted from an image, so the function immediately returns without creating volumes. `VOLSTIME=()` initializes an array to store timestamps related to the creation of Cinder volumes and calls the `createResources` function with several arguments: `$NOVMS` (number of virtual machines), `VOLSTATS` (statistics related to vol status), `VOLUME` (prefix for the vol name),`NONE` (placeholder), `VOLSTIME` (array to store timestamps), `id` (column to retrieve the vol ID), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder create` command specifies the image ID `$IMGID`, availability zone, vol name and vol size `$VOLSIZE`. The vol name is constructed using the prefix `${RPRE}RootVol_VM` followed by an index `$no`|
|delete |1754 - 1761|  `deleteNets() {   if test -n "$SECONDNET"; then     deleteResources NETSTATS SECONDNET "" $NETTIMEOUT neutron net-delete   fi   deleteResources NETSTATS NET "" $NETTIMEOUT neutron net-delete   deleteResources NETSTATS JHNET "" $NETTIMEOUT neutron net-delete }` |  handles the deletion of networks in the OpenStack environment, including main network for VMs and any secondary networks if specified. It checks if the variable `$SECONDNET` is not empty, which means there is a secondary network that needs to be deleted, so it proceeds with deleting it by calling the `deleteResources` function to delete the secondary network. The following parameters are specified: `NETSTATS` (statistics related to network status), `SECONDNET` (prefix for the secondary network name), `""` (placeholder), `$NETTIMEOUT` (timeout value for the operation). The actual `neutron net-delete` command deletes the network.
||2003 -2006| `deleteJHVols(){deleteResources VOLSTATS JHVOLUME "" $CINDERTIMEOUT cinder delete}`| deletes Cinder volumes that match the specified prefix for the volume name `JHVOLUME` by calling the  `deleteResources` function with several arguments and using the cinder delete command: `VOLSTATS` (statistics related to volume status), `JHVOLUME` (prefix for the volume name), `""`(placeholder), `$CINDERTIMEOUT` (timeout value for the operation), `cinder delete` to delete the volumes|
||2024 - 2028|`deleteVols() {if test -n "$BOOTFROMIMAGE"; then return 0; fi   deleteResources VOLSTATS VOLUME "" $CINDERTIMEOUT cinder delete }`|deletes Cinder volumes associated with virtual machines, unless the virtual machines are configured to boot from an image than it returns without performing any deletion checks if the variable $BOOTFROMIMAGE is not empty. If it is not empty, it means the virtual machines are configured to boot from an image, so the function returns early without attempting to delete volumes. It calls the `deleteResources` function with several arguments: `VOLSTATS` (statistics related to vol status), `VOLUME` (prefix for the vol name)
`""` (placeholder), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder delete` command deletes the volumes|
|flavor-show
|floatingip-create
|floatingip-delete
|floatingip-list
|image-show
|issue
|keypair-add |2030 - 2065| `createKeypairs_old() {   UMASK=$(umask)   umask 0077   ostackcmd_tm NOVASTATS $NOVATIMEOUT nova keypair-add ${RPRE}Keypair_JH \|\| return 1   echo "$OSTACKRESP" > $DATADIR/${RPRE}Keypair_JH.pem   KEYPAIRS+=( "${RPRE}Keypair_JH" )   ostackcmd_tm NOVASTATS $NOVATIMEOUT nova keypair-add ${RPRE}Keypair_VM \|\| return 1   echo "$OSTACKRESP" > $DATADIR/${RPRE}Keypair_VM.pem   KEYPAIRS+=( "${RPRE}Keypair_VM" )   umask $UMASK }  createKeyPair() {   echo -n "$1 "   if test ! -r $DATADIR/$1; then     ssh-keygen -q -C $1@$HOSTNAME -t $KPTYPE -N "" -f $DATADIR/$1 \|\| return 1   fi   ostackcmd_tm NOVASTATS $NOVATIMEOUT nova keypair-add --pub-key $DATADIR/$1.pub $1   RC=$?   if test $RC != 0; then     # The most common error is that the keypair with the name already exists     ostackcmd_tm_retry NOVASTATS $NOVATIMEOUT nova keypair-delete $1     return 1   fi   KEYPAIRS+=( "$1" ) }  createKeypairs() {   echo -n "New KEYPAIR: "   createKeyPair ${RPRE}Keypair_JH \|\| { echo; return 1; }   createKeyPair ${RPRE}Keypair_VM   echo }`| `createKeypairs_old()`: generates two key pairs using the nova keypair-add command. It sets a stricter umask before creating the key pairs to ensure that the permissions on the generated private key files are limited. The generated private keys are saved to files in the specified directory (`$DATADIR`). The names of the key pairs are `${RPRE}Keypair_JH` and `${RPRE}Keypair_VM`. The names of the key pairs are stored in the `KEYPAIRS` array for later use.`createKeyPair()`: This function creates a single key pair. If the corresponding public key file does not exist in the specified directory (`$DATADIR`), it generates a new key pair using ssh-keygen. It then uses nova keypair-add to upload the public key to OpenStack. If the key pair creation fails, it attempts to delete any existing key pair with the same name and returns an error. `createKeypairs()`: This function orchestrates the creation of key pairs. It first prints a message indicating that new key pairs are being created. Then, it calls createKeyPair twice, once for each key pair (`${RPRE}Keypair_JH` and `${RPRE}Keypair_VM`). If the creation of either key pair fails, it prints an error message and returns a non-zero exit status. Otherwise, it prints a newline to indicate the completion of the key pair creation process.
|keypair-delete | 2067 - 2073| `deleteKeypairs(){ deleteResources NOVASTATS KEYPAIR "" $NOVATIMEOUT nova keypair-delete #rm ${RPRE}Keypair_VM.pem #rm ${RPRE}Keypair_JH.pem }` | `deleteKeypairs()` is responsible for deleting key pairs from the OpenStack environment. It utilizes the `deleteResources` function to delete key pairs using the nova keypair-delete command. The function takes care of deleting all key pairs associated with the specified prefix `${RPRE}`. Additionally, it may include commands to remove the corresponding private key files (commented out in this snippet).
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
|port-create
|port-delete
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

|Resource-list |Lines in Code	|Code	| Description |
|----------|----------|----------|----------|	
|All	| 1484 - 1595|||
|waitDELLBAAS
|waitJHPORT
|waitJHVM
|waitJHVOLUME |1996 - 2001 | `waitJHVols(){ waitlistResources VOLSTATS JHVOLUME VOLCSTATS JVOLSTIME "available" "NA" $VOLSTATCOL $CINDERTIMEOUT cinder list handleWaitErr "JH volumes" VOLSTATS $CINDERTIMEOUT cinder show}`| calls the `waitlistResources` function with several arguments and this function waits for Cinder volumes to reach a specific state 'available' before proceeding. the funcion uses the cinder list command to check the status of volumes. After waiting for the volumes, the `handleWaitErr` function is called, where arguments such as the label "JH volumes", statistics related to volume status, a timeout value are passed and the command `cinder show`. this is how any errors that occur during the waiting process are handled.
|waitLBAAS | 457 - 461 | `LBWAIT=""  if test -n "$OPENSTACKCLIENT" -a -n "$LOADBALANCER"; then    openstack loadbalancer member create --help \| grep -- --wait >/dev/null 2>&1    if test $? == 0; then LBWAIT="--wait"; fi  fi`| checks if both the variables `$OPENSTACKCLIENT` and `$LOADBALANCER` are not empty. If they are not empty, it uses the `openstack loadbalancer member create --help` command to check if the `--wait` option is available. If the `--wait` option is found, it sets the variable `$LBWAIT` to `"--wait"`. This variable can be used later to control the behavior of a subsequent command related to load balancer member creation.|
|waitVM
|waitVols|2016 -2022|`waitVols() {   if test -n "$BOOTFROMIMAGE"; then return 0; fi   #waitResources VOLSTATS VOLUME VOLCSTATS VOLSTIME "available" "NA" "status" $CINDERTIMEOUT cinder show   waitlistResources VOLSTATS VOLUME VOLCSTATS VOLSTIME "available" "NA" $VOLSTATCOL $CINDERTIMEOUT cinder list   handleWaitErr "Volumes" VOLSTATS $CINDERTIMEOUT cinder show }`| ensures that Cinder volumes are available before proceeding with further actions, unless the VMs are configured to boot from an image by checking if the variable `$BOOTFROMIMAGE` is not empty, which would mean the VMs are configured to boot from an image and the func returns early without waiting for volumes, otherwise it calls the `waitlistResources` function with several arguments and waits for Cinder volumes to reach the `available` state before proceeding. The actual `cinder list` command is used to check the status of vols. If any errors occur during the waiting process the `handleWaitErr` function is called and the label `Volumes`, statistics related to vol status, a timeout value, and the `cinder show` command are passed



### BENCHMARKS

* Regex:	```/^(4000pi|iperf3|ssh|totDur|LBconn|ping|fioBW|fiokIOPS|fioLat10ms)$/```
* Tag/Label:	cmd / command

| Name/`cmd`    | `method`                                                                                                                                                   | `duration`                             | `return_code`                                                                                        | Lines in Code                                                                                                                                                                                                                                                                                           	                                                                                                                                                                                                                                                                                                                          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|				
| All           |                                                                                                                                                            |                                        |
| 4000pi        | (`JHVM$JHNO`) *TODO*                                                                                                                                       | (`$BENCH`) *TODO*                      | `0`                                                                                                  | [L3242-L3262](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3242-L3262)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | On each JumpHost VM (var `$NOAZS`) calculate 4k digits of Pi (`{ TIMEFORMAT=%2U; time echo 'scale=4000; 4*a(1)' \| bc -l; }`) and measure time. Write result to log file.                                                                                                                                                                                                                                                                              |
| LBconn			     | Number of VMs to create (beyond #AZ JumpHosts, def: 12) (`$NOVMS`)                                                                                         | Total duration of sending all requests |                                                                                                      | [L2598-L2612](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2598-L2612), (the same in [L2628-L2642](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L2628-L2642) )                                                                                                                                                                                                                                                                                                    | For the number of LBs (var `$NOVMS`) send the request `curl -m4 http://$LBIP/hostname 2>/dev/null` and measure the total duration. Round Robin -> each server gets one request. Send duration (and possible errors) to Telegraf.                                                                                                                                                                                                                       |
| fioBW			      |                                                                                                                                                            |                                        |                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| fioLat10ms			 |                                                                                                                                                            |                                        |                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| fiokIOPS			   |                                                                                                                                                            |                                        |                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| iperf3        | *TODO* (`s$VM`)                                                                                                                                            | *TODO* (`s$VM`)                        | 0                                                                                                    | [L3426-L3494](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3426-L3494)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | performs iperf3 tests between multiple hosts (var `$NONETS`). It iterates through each pair of source and target hosts, connects to each target host, and runs iperf3 tests to measure the network bandwidth, CPU utilization, and other metrics. The results are then displayed and optionally logged. Additionally handles retries if the initial test fails: `Creates Waitscript` First it creates a bash script named `${RPRE}wait` that waits for a specified command to become available on the system. Then it iterates over each VM to conduct iperf3 tests. It determines the source (`SRC`) and target (`TGT`) IP addresses for each test and ensures that the `SRC` and `TGT` are valid and not empty. Then it retrieves the floating IP address (`FLT`) associated with the target VM. It sets up SSH connectivity to the floating IP address and copies the `${RPRE}wait` script to the target. It executes iperf3 tests between the source and target using SSH, collecting the results in JSON format (`IPJSON`). `Handling Retries` if the initial iperf3 test fails, it retries after a brief delay (sleep 16). `Parsing and Logging Results`the JSON output of iperf3 tests is parsed to extract bandwidth information for sending and receiving data, as well as CPU utilization. Then it logs this output to a specified log file (`$LOGFILE`). It also logs the results to a Grafana server for monitoring. `Cleanup` the `${RPRE}wait` script is removed after completing all tests. `Output` the results of each iperf3 test are printed, including the source and target IP addresses, bandwidth, and CPU utilization.                                                                                         |
| ping		        | `stats`                                                                                                                                                    | `$FPRETRY`                             | `$FPERR`                                                                                             | [L4203-L4205](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4203-L4205), [L4219-L4220](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4219-L4220), [L4373-L4384](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4373-L4384), [L4385-L4391](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4385-L4391) | Execute function [fullconntest()](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3346-L3424) which performs connectivity tests. Each VM pings each VM. FPRETRY: Number of retried pings, FPERR: Number of failed pings                                                                                                                                                  |
| ping		        | `errors`                                                                                                                                                   | `1`                                    | `$FPERR`                                                                                             | [L4215](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4215)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | See above                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ping		        | `retries`                                                                                                                                                  | `1`                                    | `$FPRETRY`                                                                                           | [L4216](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4216)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | See above                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ssh	          |                                                                                                                                                            |                                        |                                                                                                      | [L3102-L3176](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3102-L3176)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| totDur        | Max cycle time (`$MAXCYC`), an calculated upper bound (including magic numbers) how long one iteration may take depending on the tasks which are performed | Relative performance (`$RELPERF`)      | Number of slow iterations, which is incremented by one when `$THISRUNTIME` is greater than `$MAXCYC` | [L4455-L4484](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L4455-L4484)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Log measured relative duration of current iteration (var `$RELPERF`, relative performance/time; calculated `echo "scale=2; 10*$THISRUNTIME/$MAXCYC" \| bc -l`). Send alert if performance of one cycle is slow. See commit [7fa38](https://github.com/SovereignCloudStack/openstack-health-monitor/commit/7fa38f9f86280bc409783e81c7b6cd0345dca530). FYI: `$TOTTIME` is the overall runtime summing up all iterations and is present in overall stats. |			



* Regex:	`/^(4000pi|iperf3|ssh|totDur|LBconn|ping|fioBW|fiokIOPS|fioLat10ms)$/`
* Tag/Label:	cmd / command

|Cloud-list |Lines in Code |Code	|Description|
|----------|----------|----------|----------|				
|All
|4000pi			
|LBconn			
|fioBW			
|fioLat10ms			
|fiokIOPS			
|iperf3| 3426 - 3494|| performs iperf3 tests between multiple hosts. It iterates through each pair of source and target hosts, connects to each target host, and runs iperf3 tests to measure the network bandwidth, CPU utilization, and other metrics. The results are then displayed and optionally logged. Additionally handles retries if the initial test fails: `Creates Waitscript` First it creates a bash script named `${RPRE}wait` that waits for a specified command to become available on the system. Then it iterates over each VM to conduct iperf3 tests. It determines the source (`SRC`) and target (`TGT`) IP addresses for each test and ensures that the `SRC` and `TGT` are valid and not empty. Then it retrieves the floating IP address (`FLT`) associated with the target VM. It sets up SSH connectivity to the floating IP address and copies the `${RPRE}wait` script to the target. It executes iperf3 tests between the source and target using SSH, collecting the results in JSON format (`IPJSON`). `Handling Retries` if the initial iperf3 test fails, it retries after a brief delay (sleep 16). `Parsing and Logging Results`the JSON output of iperf3 tests is parsed to extract bandwidth information for sending and receiving data, as well as CPU utilization. Then it logs this output to a specified log file (`$LOGFILE`). It also logs the results to a Grafana server for monitoring. `Cleanup` the `${RPRE}wait` script is removed after completing all tests. `Output` the results of each iperf3 test are printed, including the source and target IP addresses, bandwidth, and CPU utilization.
|
|ping		|	
|ssh	|3102 - 3176|		
|totDur |			


## Parent Functions

### ostackcmd_id()
* Lines in Code: 1024 - 1080
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
* Lines in Code: 1145 - 1176 [link:https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1145-L1176]
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
## SCOL, state2col(), STATE, FAIEDNO
* Lines in Code: 1178 - 1191 [link:https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L1178-L1191]
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
### colstat

* Lines in Code: 1392 - 1412
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
* Lines in Code: 1207 - 1252
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
* Lines in Code: 1254 - 1318
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

* Lines in Code: 1320- 1390
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

* Lines in Code: 1414 - 1482
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

* Lines in Code: 1484 - 1595
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
