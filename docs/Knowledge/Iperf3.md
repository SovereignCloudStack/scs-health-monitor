# Iperf3

The Iperf3 is a test performed by a client-server-constelation. Find the Docs [here][link].

[link]:https://iperf.fr/iperf-doc.php

## Test Iperf3 on your own machine  
First install iperf3 locally

Then you can create an iperf3-server with

``` 
iperf3 -s   
```
that listens on a certain port:
```
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
```

Next you can create an iperf3-client that addresses that port on localhost:
```
iperf3 -c localhost -p 5201
```

and you will receive the tcp-test results on both sides:

client:
```
Connecting to host localhost, port 5201
[  5] local 127.0.0.1 port 53216 connected to 127.0.0.1 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  3.86 GBytes  33.2 Gbits/sec    0   3.18 MBytes       
[  5]   1.00-2.00   sec  3.83 GBytes  32.9 Gbits/sec    0   3.18 MBytes       
[  5]   2.00-3.00   sec  2.96 GBytes  25.4 Gbits/sec    1   3.18 MBytes       
[  5]   3.00-4.00   sec  3.08 GBytes  26.5 Gbits/sec    0   3.18 MBytes       
[  5]   4.00-5.00   sec  3.23 GBytes  27.8 Gbits/sec    0   3.18 MBytes       
[  5]   5.00-6.00   sec  3.20 GBytes  27.5 Gbits/sec    0   3.18 MBytes       
[  5]   6.00-7.00   sec  3.15 GBytes  27.0 Gbits/sec    0   3.18 MBytes       
[  5]   7.00-8.00   sec  3.21 GBytes  27.5 Gbits/sec    0   3.18 MBytes       
[  5]   8.00-9.00   sec  3.32 GBytes  28.5 Gbits/sec    1   3.18 MBytes       
[  5]   9.00-10.00  sec  3.36 GBytes  28.9 Gbits/sec    0   3.18 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  33.2 GBytes  28.5 Gbits/sec    2             sender
[  5]   0.00-10.04  sec  33.2 GBytes  28.4 Gbits/sec                  receiver
```

server:
```
Accepted connection from 127.0.0.1, port 53210
[  5] local 127.0.0.1 port 5201 connected to 127.0.0.1 port 53216
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-1.00   sec  3.75 GBytes  32.2 Gbits/sec                  
[  5]   1.00-2.00   sec  3.79 GBytes  32.5 Gbits/sec                  
[  5]   2.00-3.00   sec  3.00 GBytes  25.8 Gbits/sec                  
[  5]   3.00-4.00   sec  3.06 GBytes  26.3 Gbits/sec                  
[  5]   4.00-5.00   sec  3.26 GBytes  28.0 Gbits/sec                  
[  5]   5.00-6.00   sec  3.20 GBytes  27.5 Gbits/sec                  
[  5]   6.00-7.00   sec  3.13 GBytes  26.9 Gbits/sec                  
[  5]   7.00-8.00   sec  3.20 GBytes  27.5 Gbits/sec                  
[  5]   8.00-9.00   sec  3.32 GBytes  28.5 Gbits/sec                  
[  5]   9.00-10.00  sec  3.39 GBytes  29.1 Gbits/sec                  
[  5]  10.00-10.04  sec   102 MBytes  19.9 Gbits/sec                  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-10.04  sec  33.2 GBytes  28.4 Gbits/sec                  receiver
```

If you want to test the udp-connection you need to type the following on the client-side:
```
iperf3 -c localhost -p 5201 -u
```
and get:

client:
```
Connecting to host localhost, port 5201
[  5] local 127.0.0.1 port 59453 connected to 127.0.0.1 port 5201
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   1.00-2.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   2.00-3.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   3.00-4.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   4.00-5.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   5.00-6.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   6.00-7.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   7.00-8.00   sec   128 KBytes  1.05 Mbits/sec  4  
[  5]   8.00-9.01   sec   128 KBytes  1.04 Mbits/sec  4  
[  5]   9.01-10.00  sec   128 KBytes  1.06 Mbits/sec  4  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec  1.25 MBytes  1.05 Mbits/sec  0.000 ms  0/40 (0%)  sender
[  5]   0.00-10.04  sec  1.25 MBytes  1.04 Mbits/sec  1.212 ms  0/40 (0%)  receiver

iperf Done.
```

server:
```
Accepted connection from 127.0.0.1, port 39768
[  5] local 127.0.0.1 port 5201 connected to 127.0.0.1 port 59453
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec   128 KBytes  1.05 Mbits/sec  0.037 ms  0/4 (0%)  
[  5]   1.00-2.00   sec   128 KBytes  1.05 Mbits/sec  0.066 ms  0/4 (0%)  
[  5]   2.00-3.00   sec   128 KBytes  1.05 Mbits/sec  0.104 ms  0/4 (0%)  
[  5]   3.00-4.00   sec   128 KBytes  1.05 Mbits/sec  0.140 ms  0/4 (0%)  
[  5]   4.00-5.00   sec   128 KBytes  1.05 Mbits/sec  0.156 ms  0/4 (0%)  
[  5]   5.00-6.00   sec   128 KBytes  1.05 Mbits/sec  0.133 ms  0/4 (0%)  
[  5]   6.00-7.00   sec   128 KBytes  1.05 Mbits/sec  0.115 ms  0/4 (0%)  
[  5]   7.00-8.00   sec   128 KBytes  1.05 Mbits/sec  0.100 ms  0/4 (0%)  
[  5]   8.00-9.00   sec   128 KBytes  1.05 Mbits/sec  0.082 ms  0/4 (0%)  
[  5]   9.00-10.00  sec   128 KBytes  1.05 Mbits/sec  1.212 ms  0/4 (0%)  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.04  sec  1.25 MBytes  1.04 Mbits/sec  1.212 ms  0/40 (0%)  receiver
```

## Script api_monitor.sh Breakdown -> concerning iperf3:

[cat >${RPRE}wait.. L3426-L3441](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3426-L3441):

* creates a temporary script ${RPRE}wait that  is made executable and checks for the availability of a specified command `\$1` (e.g. iperf3).
* waits for the system boot to finish if necessary and retries for up to 100 seconds if the command is not found



[#calcRedirs.. L3441-L3462](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3443-L3462):

  * calcRedirs: Do tests from last host in net and connect to 1st hosts in 1st/2nd/... net
  * extracts the relevant redirection information for network tests and gets the port number (`pno`), beginning with the last 
  * iterates through a list of VMs (`NONETS` is the total number of networks)
  * sets `TGT` (target IP) and `SRC` (source IP) for each test, ensuring they are not the same and are properly defined

  ```
  red=${REDIRS[$((NOAZS-1))]}
red=$(echo "$red" | grep -v '^$' | tail -n1)
pno=${red#*tcp,}
pno=${pno%%,*}
echo -n "IPerf3 tests:"
for VM in $(seq 0 $((NONETS-1))); do
  TGT=${IPS[$VM]}
  if test -z "$TGT"; then TGT=${IPS[$(($VM+$NONETS))]}; fi
  SRC=${IPS[$(($VM+$NOVMS-$NONETS))]}
  if test -z "$SRC"; then SRC=${IPS[$(($VM+$NOVMS-2*$NONETS))]}; fi
  if test -z "$SRC" -o -z "$TGT" -o "$SRC" = "$TGT"; then
    echo "#ERROR: Skip test $SRC <-> $TGT"
    if test -n "$LOGFILE"; then echo "IPerf3: ${SRC}-${TGT}: skipped" >>$LOGFILE; fi
    continue
  fi
  ```

[FLT=${FLOATS.. L3463-L3477](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3463-L3477):

* copies the temporary wait script to the target floating IP (`FLT`) of the VM.
Logs the ssh command to a logfile if `LOGFILE` is defined
* runs the wait script and the iPerf3 test from the source VM to the target VM, capturing the output in JSON format
* it retries after 16 seconds if the initial test fails

```
    FLT=${FLOATS[$(($VM%$NOAZS))]}
    #echo -n "Test ($SRC,$(($VM+$NOVMS-$NONETS)),$FLT/$pno)->$TGT: "
    scp -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -P $pno -p ${RPRE}wait ${DEFLTUSER}@$FLT: >/dev/null
    if test -n "$LOGFILE"; then echo "ssh -o \"UserKnownHostsFile=~/.ssh/known_hosts.$RPRE\" -o \"PasswordAuthentication=no\" -o \"StrictHostKeyChecking=no\" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT iperf3 -t5 -J -c $TGT" >> $LOGFILE; fi
    IPJSON=$(ssh -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT "./${RPRE}wait iperf3; iperf3 -t5 -J -c $TGT")
    if test $? != 0; then
      # Clients may need more startup time
      echo -n " retry "
      sleep 16
      IPJSON=$(ssh -o "UserKnownHostsFile=~/.ssh/known_hosts.$RPRE" -o "PasswordAuthentication=no" -o "StrictHostKeyChecking=no" -i $DATADIR/${KEYPAIRS[1]} -p $pno ${DEFLTUSER}@$FLT "iperf3 -t5 -J -c $TGT")
      if test $? != 0; then
	log_grafana "iperf3" "s$VM" "0" "1"
        continue
      fi
    fi
```

[if test -n "$LOGFILE".. L3478-L3490](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3478-L3490):

* parses the JSON output to extract the send and receive bandwidths, and the CPU utilization percentages for both the host and remote machines
* prints and logs the results
* adds the bandwidth results to the BANDWIDTH array
* logs the bandwidth data to Grafana for visualization

```
    if test -n "$LOGFILE"; then echo "$IPJSON" >> $LOGFILE; fi
    SENDBW=$(($(printf "%.0f\n" $(echo "$IPJSON" | jq '.end.sum_sent.bits_per_second'))/1048576))
    RECVBW=$(($(printf "%.0f\n" $(echo "$IPJSON" | jq '.end.sum_received.bits_per_second'))/1048576))
    HUTIL=$(printf "%.1f%%\n" $(echo "$IPJSON" | jq '.end.cpu_utilization_percent.host_total'))
    RUTIL=$(printf "%.1f%%\n" $(echo "$IPJSON" | jq '.end.cpu_utilization_percent.remote_total'))
    echo -e " ${SRC} <-> ${TGT}: ${BOLD}$SENDBW Mbps $RECVBW Mbps $HUTIL $RUTIL${NORM}"
    if test -n "$LOGFILE"; then echo -e "IPerf3: ${SRC}-${TGT}: $SENDBW Mbps $RECVBW Mbps $HTUIL $RUTIL" >>$LOGFILE; fi
    BANDWIDTH+=($SENDBW $RECVBW)
    SBW=$(echo "scale=2; $SENDBW/1000" | bc -l)
    RBW=$(echo "scale=2; $RECVBW/1000" | bc -l)
    log_grafana "iperf3" "s$VM" "$SBW" 0
    log_grafana "iperf3" "r$VM" "$RBW" 0
  done
```


[rm ${RPRE}wait.. L3491-L3493](https://github.com/SovereignCloudStack/openstack-health-monitor/blob/084e8960d9348af7b3c5c9927a1ebaebf4be48f9/api_monitor.sh#L3491-L3493):

* deletes the temporary wait script
* outputs a backspace to remove the trailing space or character
```
  rm ${RPRE}wait
  echo -en "\b"
```

