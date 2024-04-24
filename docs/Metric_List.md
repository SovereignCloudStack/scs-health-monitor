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
|create |1742 - 1752 | `createNets() {  ERC=0  createResources 1 NETSTATS JHNET NONE NONE "" id $NETTIMEOUT nutron net-create "${RPRE}NET_JH" \|\| ERC=$?  if test $NONAZS -le 1; then    createResources $NONETS NETSTATS NET NONE NONE "" id $NETTIMEOUT neutron net-create "${RPRE}NET_VM_\$no" \|\|ERC=$?  else    createResources $NONETS NETSTATS NET NONE NONE "" id $NETTIMEOUT neutron net-create --availability-zone-hint"\${NAZS[\$((\$no%$NONAZS))]}" "${RPRE}NET_VM_\$no" \|\| ERC=$?  fi  return $ERC}`
||1989 - 1993| `createJHVols(){ JVOLSTIME=()   createResources $NOAZS VOLSTATS JHVOLUME NONE NONE JVOLSTIME id $CINDERTIMEOUT cinder create --image-id $JHIMGID --availability-zone \${VAZS[\$VAZN]} --name ${RPRE}RootVol_JH\$no $JHVOLSIZE }`| responsible for creating Cinder volumes: initializes an array `JVOLSTIME=()` to store timestamps related to the creation of Cinder volumes and calls the `createResources` function with several arguments to create Cinder volumes using the cinder create command: `$NOAZS` (Number of availability zones), `VOLSTATS` (statistics related to volume status), `JHVOLUME` (prefix for the vol name), `NONE` (placeholder), `JVOLSTIME` (array of timestamps) `id` (column to retrieve the vol ID), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder create` command to create the volume specifies the image ID `$JHIMGID`, availability zone, vol name and vol size `$JHVOLSIZE`. The vol name is constructed using the prefix `${RPRE}RootVol_JH` followed by an index `$no`| creates networks for both the Jump Host and VMs in the OpenStack environment, handles any errors and returns exit codes by caslling the `createResources` function to create a network for the JH and specifing the following parameters: `1` (number of networks to create), `NETSTATS` (statistics related to network status), `JHNET` (prefix for the network name), `NONE` (placeholder), `id` (column to retrieve the network ID), `$NETTIMEOUT` (timeout value for the operation), `neutron net-create "${RPRE}NET_JH"`is the actual `neutron` command to create the network for the JH constructing the network name using the prefix `${RPRE}NET_JH`. Then the creation of networks for VM is handled with an if statementthat checks whether there is only one availability zone (NONAZS <= 1) so it would not specify an availability zone hint. Else it specifies an availability zone hint based on the available availability zones. The return `$ERC` statement returns the value that indicates whether any errors occurred during the network creation process|
||2008 - 2013|`createVols() { if test -n "$BOOTFROMIMAGE"; then return 0; fi VOLSTIME=() createResources $NOVMS VOLSTATS VOLUME NONE NONE VOLSTIME id $CINDERTIMEOUT cinder create --image-id $IMGID --availability-zone \${VAZS[\$VAZN]} --name ${RPRE}RootVol_VM\$no $VOLSIZE}`| creates Cinder volumes for virtual machines, except when the virtual machines are booted from an image therefore it checks if the variable `$BOOTFROMIMAGE` is not empty, which would mean the virtual machines should be booted from an image, so the function immediately returns without creating volumes. `VOLSTIME=()` initializes an array to store timestamps related to the creation of Cinder volumes and calls the `createResources` function with several arguments: `$NOVMS` (number of virtual machines), `VOLSTATS` (statistics related to vol status), `VOLUME` (prefix for the vol name),`NONE` (placeholder), `VOLSTIME` (array to store timestamps), `id` (column to retrieve the vol ID), `$CINDERTIMEOUT` (timeout value for the operation). The actual `cinder create` command specifies the image ID `$IMGID`, availability zone, vol name and vol size `$VOLSIZE`. The vol name is constructed using the prefix `${RPRE}RootVol_VM` followed by an index `$no`|
|delete |2003 -2006| `deleteJHVols(){deleteResources VOLSTATS JHVOLUME "" $CINDERTIMEOUT cinder delete}`| deletes Cinder volumes that match the specified prefix for the volume name `JHVOLUME` by calling the  `deleteResources` function with several arguments and using the cinder delete command: `VOLSTATS` (statistics related to volume status), `JHVOLUME` (prefix for the volume name), `""`(placeholder), `$CINDERTIMEOUT` (timeout value for the operation), `cinder delete` to delete the volumes|
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
|iperf3| 3426 - 3494| `#Do iperf3 tests iperf3test() { cat >${RPRE}wait <<EOT #!/bin/bash let MAXW=100 if test ! -f /var/lib/cloud/instance/boot-finished; then sleep 5; sync; fi while test \$MAXW -ge 1; do if type -p "\$1">/dev/null; then exit 0; fi let MAXW-=1 sleep 1 if test ! -f /var/lib/cloud/instance/boot-finished; then sleep 1; fi done exit 1 EOT chmod +x ${RPRE}wait #Do tests from last host in net and connect to 1st hosts in 1st/2nd/... net #calcRedirs red=${REDIRS[$((NOAZS-1))]} #red=$(echo $red \| cut -d " " -f $((NONETS+1))) #red=$(echo "$red" \| grep -v '^$' \| tail -n2 \| head -n1) red=$(echo "$red" \| grep -v '^$' \| tail -n1) #echo "$red" pno=${red#*tcp,} pno=${pno%%,*} #echo "Redirect: ${REDIRS[0]} $red $pno" echo -n "IPerf3 tests:" for VM in $(seq 0 $((NONETS-1))); do TGT=${IPS[$VM]} if test -z "$TGT"; then TGT=${IPS[$(($VM+$NONETS))]}; fi   SRC=${IPS[$(($VM+$NOVMS-$NONETS))]}   if test -z "$SRC"; then SRC=${IPS[$(($VM+$NOVMS-2*$NONETS))]}; fi   if test -z "$SRC" -o -z "$TGT" -o "$SRC" = "$TGT"; then     echo "#ERROR: Skip test $SRC <-> $TGT"     if test -n "$LOGFILE"; then echo "IPerf3: ${SRC}-${TGT}: skipped" >>$LOGFILE; fi     continue   fi   FLT=${FLOATS[$(($VM%$NOAZS))]}   #echo -n "Test ($SRC,$(($VM+$NOVMS-$NONETS)),$FLT/$pno)->$TGT: "   scp -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -P $pno -p ${RPRE}wait ${DEFLTUSER}@$FLT: >/dev/null   if test -n "$LOGFILE"; then echo "ssh -o \"UserKnownHostsFile=~/.ssh/known_hosts.$RPRE\" -o \"PasswordAuthentication=no\" -o \"StrictHostKeyChecking=no\" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT iperf3 -t5 -J -c $TGT" >> $LOGFILE; fi   IPJSON=$(ssh -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT "./${RPRE}wait iperf3; iperf3 -t5 -J -c $TGT")   if test $? != 0; then     # Clients may need more startup time     echo -n " retry "     sleep 16     IPJSON=$(ssh -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT "iperf3 -t5 -J -c $TGT")     if test $? != 0; then log_grafana "iperf3" "s$VM" "0" "1"       continue     fi fi if test -n "$LOGFILE"; then echo "$IPJSON" >> $LOGFILE; fi SENDBW=$(($(printf "%.0f\n" $(echo "$IPJSON" \| jq '.end.sum_sent.bits_per_second'))/1048576)) RECVBW=$(($(printf "%.0f\n" $(echo "$IPJSON" \| jq '.end.sum_received.bits_per_second'))/1048576)) HUTIL=$(printf "%.1f%%\n" $(echo "$IPJSON" \| jq '.end.cpu_utilization_percent.host_total')) RUTIL=$(printf "%.1f%%\n" $(echo "$IPJSON" \| jq '.end.cpu_utilization_percent.remote_total')) echo -e " ${SRC} <-> ${TGT}: ${BOLD}$SENDBW Mbps $RECVBW Mbps $HUTIL $RUTIL${NORM}" if test -n "$LOGFILE"; then echo -e "IPerf3: ${SRC}-${TGT}: $SENDBW Mbps $RECVBW Mbps $HTUIL $RUTIL" >>$LOGFILE; fi BANDWIDTH+=($SENDBW $RECVBW) SBW=$(echo "scale=2; $SENDBW/1000" \| bc -l) RBW=$(echo "scale=2; $RECVBW/1000" \| bc -l) log_grafana "iperf3" "s$VM" "$SBW" 0 log_grafana "iperf3" "r$VM" "$RBW" 0 done rm ${RPRE}wait echo -en "\b"} ` | performs iperf3 tests between multiple hosts. It iterates through each pair of source and target hosts, connects to each target host, and runs iperf3 tests to measure the network bandwidth, CPU utilization, and other metrics. The results are then displayed and optionally logged. Additionally handles retries if the initial test fails|
|ping		|	
|ssh	|3102 - 3176|		
|totDur |			


## Parent Functions

### waitlistResources()

* Lines in Code: 1484 - 1595
* Purpose: a versatile and robust tool for waiting for resources to reach a desired state in an OpenStack environment
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



