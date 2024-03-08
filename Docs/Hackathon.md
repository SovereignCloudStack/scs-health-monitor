# dNation KaaS Hackathon in Bratislava 5.3.2024 - 6.3.2024

## Test openstack health monitor performance test

1) Cloning repository from [here](https://github.com/SovereignCloudStack/openstack-health-monitor)
2) Add the following environment variables to the start of run_gx_scs.sh file
```bash
export OS_AUTH_TYPE=v3applicationcredential
export OS_AUTH_URL=https://api.gx-scs.sovereignit.cloud:5000
export OS_IDENTITY_API_VERSION=3
export OS_REGION_NAME="RegionOne"
export OS_INTERFACE=public
export OS_APPLICATION_CREDENTIAL_ID=<credential_ID>
export OS_APPLICATION_CREDENTIAL_SECRET=<credential_secret>
```
3) Update the docker file:
```
# add this to the command
ENTRYPOINT ["/run_gx_scs.sh"]

# update entrypoint as follows
run_gx_scs.sh
```

Example output: 
```
ACTIVE Slow 21.00s: myopenstack loadbalancer member create --wait --name APIMonitor_1709647006_Member_5 --address 10.250.4.41 --protocol-port 80 4082f2d4-b106-45f1-ab1a-135e31c5a3d6 => 0 +---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| address             | 10.250.4.41                          |
| admin_state_up      | True                                 |
| created_at          | 2024-03-05T14:33:54                  |
| id                  | 37dfe34a-404f-4a15-a2fa-c4b2a46f9d31 |
| name                | APIMonitor_1709647006_Member_5       |
| operating_status    | ONLINE                               |
| project_id          | 476672f1023b4bac8837f95a76881757     |
| protocol_port       | 80                                   |
| provisioning_status | ACTIVE                               |
| subnet_id           | None                                 |
| updated_at          | 2024-03-05T14:34:13                  |
| weight              | 1                                    |
| monitor_port        | None                                 |
| monitor_address     | None                                 |
| backup              | False                                |
| tags                |                                      |
+---------------------+--------------------------------------+
```

4) Build the docker image using "docker build -t oshm ."
5) Create a container for the docker image using "docker run -t oshm ."
6) Wait until the script finishes
