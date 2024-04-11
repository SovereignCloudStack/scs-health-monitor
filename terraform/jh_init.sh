#cloud-config
packages:
  - iptables
  - bc
  - fio
  - iperf3
otc:
   internalnet:
      - 10.0.0.0/16
   snat:
      masqnet:
         - INTERNALNET