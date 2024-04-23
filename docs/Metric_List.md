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
|----------|----------|----------|----------|----------|----------|
OVERVIEW					
|API calls	|Takes all connections(with return code) from selected cloud with selected command, method in current time interval	|return-code, $mycloud, $mycmd, $mymethod	|count	|``` SELECT count("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval) fill(null)```| |
|API errors	|Takes all connections(with error return code) from selected cloud with selected command, method in current time interval 	|| return-code, $mycloud, $mycmd, $mymethod	|count	|```SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval)``` ||
|API success rate	|Takes all connections subtracts the sum of counts with an error-return code and devides it through all connections filtered by selected cloud with selected command, method in current time interval  	|| return-code, $mycloud, $mycmd, $mymethod	|percent	|```SELECT ((count("return_code")-sum("return_code"))/count("return_code")) FROM "$mycloud" WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter```||	
|ssh conns	|Takes all connections(with return code) and the command ssh from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|count	|```SELECT count("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" = 'ssh') AND $timeFilter GROUP BY time($__interval) fill(null)```|
|ssh errors	|Takes all connections with an error return code and the command ssh from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod|	count	|```SELECT sum("return_code") FROM "$mycloud" WHERE ("cmd" = 'ssh') AND $timeFilter GROUP BY time($__interval)```||
|ssh success rate	|Takes all connections with cmd=ssh subtracts the sum of cmd=ssh-counts with an error-return code and devides it through all connections with cmd=ssh filtered by selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|percent	|```SELECT ((count("return_code")-sum("return_code"))/count("return_code")) FROM "$mycloud" WHERE ("cmd" = 'ssh') AND $timeFilter```||
|Resources	|Takes all connections(with return code) and the commands that match the RESOURCES-list in the $mywait-Variable from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|count	|SELECT count("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mywait$/) AND $timeFilter GROUP BY time($__interval) fill(null)|	
|Resource errors	|Takes all connections with an error return code and the commands that match the RESOURCES-list in the $mywait-Variable from selected cloud with selected method in current time interval  	|return-code, $mycloud, $mycmd, $mymethod	|count	|```SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mywait$/) AND $timeFilter GROUP BY time($__interval)```||
|iperf success rate	|Takes all connections with cmd=iperf3 subtracts the sum of cmd= iperf3-counts with an error-return code and devides it through all connections with cmd= iperf3 filtered by selected cloud with selected method in current time interval |return-code, $mycloud, $mycmd, $mymethod	|percent	|```SELECT ((count("return_code")-sum("return_code"))/count("return_code")) FROM "$mycloud" WHERE ("cmd" = 'iperf3') AND $timeFilter```||
STATS					
|API errors	|Takes all connections with an error return code from selected cloud with selected method in current time interval and grouped by method |return-code,$mycloud, $mycmd, (Group = $mymethod)|	rc	|```SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval), "cmd", "method"	```||
|Resource errors	|Takes all connections with an error return code the commands that match the RESOURCES-list in the $mywait-Variable  from selected cloud with selected method in current time interval and grouped by wait-command ||# errors	|```SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mywait$/) AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)	```|waitDELLBAAS  waitJHVM  waitJHVOLUME  waitLBAAS  WaitVM|
|Bench (ssh) errors	|Takes all connections with an Benchmark-Error (tagged by benchmark functions in shellscript) from selected cloud with selected method in current time interval and  grouped by ERR($tag_cmd) ||Errs	|```SELECT sum("return_code") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mybench$/) AND $timeFilter GROUP BY time($__interval), "cmd" fill(null)```|ERR(LBconn)  ERR(totDur)  ERR(4000pi)  ERR(fioBW)  ERR(fioLat10ms)  ERR(fiokIOPS)  ERR(iperf3)  ERR(ping)  ERR(ssh)|
PERFORMANCE					
|API response times	|Takes the mean duration from all connections(with return code) from selected cloud with selected command, method in current time interval and groups them by cmd or method||s|```SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mycmd$/ AND "method" =~ /^$mymethod$/) AND $timeFilter GROUP BY time($__interval), "cmd", "method" fill(none)```||	
|Resource wait	|Takes the mean duration all connections with the command that match the RESOURCES-list in the $mywait-Variable and the method-tags (A) ACTIVE, (B) available, (C) XDELX (D) the rest from selected cloud with selected method in current time interval and grouped by wait-command |s |(A) ```SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag = 'ACTIVE') AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)``` (B) ```SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag = 'available') AND $timeFilter GROUP BY time($__interval), "cmd" fthe method-tagill(none)``` (C) ```SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag = 'XDELX') AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)``` (D) ```SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd"::tag =~ /^$mywait$/ AND "method"::tag !~ /^(ACTIVE\|available\|XDELX)$/) AND $timeFilter GROUP BY time($__interval), "cmd"::tag, "method"::tag fill(none)``` ||
|Bench |Takes the mean duration from all connections(with return code) with commands thatr match the Bench-list in the $mybench-Variable from selected cloud with selected command, method in current time interval and groups them by cmd or method |s, Gb/s, s, %maxt*10, s*10, MB/s, IO/s, %	|```SELECT mean("duration") FROM "default"./^$mycloud$/ WHERE ("cmd" =~ /^$mybench$/) AND $timeFilter GROUP BY time($__interval), "cmd" fill(none)```||


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

* Regex: ```/^(nova|neutron|glance|cinder|token|catalog|swift|octavia)$/```
* Tag/Label: cmd/command

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
|create
|delete
|flavor-show
|floatingip-create
|floatingip-delete
|floatingip-list
|image-show
|issue
|keypair-add
|keypair-delete
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

* Regex:	```/^wait/``` 
* Tag/Label: cmd/command


|Resource-list |Lines in Code	|Code	| Description |
|----------|----------|----------|----------|	
|All	| 1484 – 1595|||
|waitDELLBAAS
|waitJHPORT
|waitJHVM
|waitJHVOLUME
|waitLBAAS | 457 – 461 | ```LBWAIT=""  if test -n "$OPENSTACKCLIENT" -a -n "$LOADBALANCER"; then    openstack loadbalancer member create --help \| grep -- --wait >/dev/null 2>&1    if test $? == 0; then LBWAIT="--wait"; fi  fi```| checks if both the variables `$OPENSTACKCLIENT` and `$LOADBALANCER` are not empty. If they are not empty, it uses the `openstack loadbalancer member create --help` command to check if the `--wait` option is available. If the `--wait` option is found, it sets the variable `$LBWAIT` to `"--wait"`. This variable can be used later to control the behavior of a subsequent command related to load balancer member creation.|
|waitVM


### BENCHMARKS

* Regex:	```/^(4000pi|iperf3|ssh|totDur|LBconn|ping|fioBW|fiokIOPS|fioLat10ms)$/```
* Tag/Label:	cmd / command

|Cloud-list |Lines in Code |Code	|Description|
|----------|----------|----------|----------|				
|All
|4000pi			
|LBconn			
|fioBW			
|fioLat10ms			
|fiokIOPS			
|iperf3| 3426-3494| ```#Do iperf3 tests iperf3test() { cat >${RPRE}wait <<EOT #!/bin/bash let MAXW=100 if test ! -f /var/lib/cloud/instance/boot-finished; then sleep 5; sync; fi while test \$MAXW -ge 1; do if type -p "\$1">/dev/null; then exit 0; fi let MAXW-=1 sleep 1 if test ! -f /var/lib/cloud/instance/boot-finished; then sleep 1; fi done exit 1 EOT chmod +x ${RPRE}wait #Do tests from last host in net and connect to 1st hosts in 1st/2nd/... net #calcRedirs red=${REDIRS[$((NOAZS-1))]} #red=$(echo $red \| cut -d " " -f $((NONETS+1))) #red=$(echo "$red" \| grep -v '^$' \| tail -n2 \| head -n1) red=$(echo "$red" \| grep -v '^$' \| tail -n1) #echo "$red" pno=${red#*tcp,} pno=${pno%%,*} #echo "Redirect: ${REDIRS[0]} $red $pno" echo -n "IPerf3 tests:" for VM in $(seq 0 $((NONETS-1))); do TGT=${IPS[$VM]} if test -z "$TGT"; then TGT=${IPS[$(($VM+$NONETS))]}; fi   SRC=${IPS[$(($VM+$NOVMS-$NONETS))]}   if test -z "$SRC"; then SRC=${IPS[$(($VM+$NOVMS-2*$NONETS))]}; fi   if test -z "$SRC" -o -z "$TGT" -o "$SRC" = "$TGT"; then     echo "#ERROR: Skip test $SRC <-> $TGT"     if test -n "$LOGFILE"; then echo "IPerf3: ${SRC}-${TGT}: skipped" >>$LOGFILE; fi     continue   fi   FLT=${FLOATS[$(($VM%$NOAZS))]}   #echo -n "Test ($SRC,$(($VM+$NOVMS-$NONETS)),$FLT/$pno)->$TGT: "   scp -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -P $pno -p ${RPRE}wait ${DEFLTUSER}@$FLT: >/dev/null   if test -n "$LOGFILE"; then echo "ssh -o \"UserKnownHostsFile=~/.ssh/known_hosts.$RPRE\" -o \"PasswordAuthentication=no\" -o \"StrictHostKeyChecking=no\" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT iperf3 -t5 -J -c $TGT" >> $LOGFILE; fi   IPJSON=$(ssh -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT "./${RPRE}wait iperf3; iperf3 -t5 -J -c $TGT")   if test $? != 0; then     # Clients may need more startup time     echo -n " retry "     sleep 16     IPJSON=$(ssh -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT "iperf3 -t5 -J -c $TGT")     if test $? != 0; then log_grafana "iperf3" "s$VM" "0" "1"       continue     fi fi if test -n "$LOGFILE"; then echo "$IPJSON" >> $LOGFILE; fi SENDBW=$(($(printf "%.0f\n" $(echo "$IPJSON" \| jq '.end.sum_sent.bits_per_second'))/1048576)) RECVBW=$(($(printf "%.0f\n" $(echo "$IPJSON" \| jq '.end.sum_received.bits_per_second'))/1048576)) HUTIL=$(printf "%.1f%%\n" $(echo "$IPJSON" \| jq '.end.cpu_utilization_percent.host_total')) RUTIL=$(printf "%.1f%%\n" $(echo "$IPJSON" \| jq '.end.cpu_utilization_percent.remote_total')) echo -e " ${SRC} <-> ${TGT}: ${BOLD}$SENDBW Mbps $RECVBW Mbps $HUTIL $RUTIL${NORM}" if test -n "$LOGFILE"; then echo -e "IPerf3: ${SRC}-${TGT}: $SENDBW Mbps $RECVBW Mbps $HTUIL $RUTIL" >>$LOGFILE; fi BANDWIDTH+=($SENDBW $RECVBW) SBW=$(echo "scale=2; $SENDBW/1000" \| bc -l) RBW=$(echo "scale=2; $RECVBW/1000" \| bc -l) log_grafana "iperf3" "s$VM" "$SBW" 0 log_grafana "iperf3" "r$VM" "$RBW" 0 done rm ${RPRE}wait echo -en "\b"} ``` | performs iperf3 tests between multiple hosts. It iterates through each pair of source and target hosts, connects to each target host, and runs iperf3 tests to measure the network bandwidth, CPU utilization, and other metrics. The results are then displayed and optionally logged. Additionally handles retries if the initial test fails|
|ping		|	
|ssh	|3102 – 3176|		
|totDur |			






