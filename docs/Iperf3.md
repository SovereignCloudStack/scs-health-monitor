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