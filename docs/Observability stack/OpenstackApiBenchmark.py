import openstack
from prometheus_client import push_to_gateway, write_to_textfile, REGISTRY
import random
import time

PROMETHEUS_URL = "localhost:30001"
PROMETHEUS_JOB_NAME = "erikBatch"
BENCHMARK_DURATION_MINUTES = 1
API_CALL_SLEEP_SECONDS_MIN = 5
API_CALL_SLEEP_SECONDS_MAX = 10

def process_bdt(os_connection, t):
    """A dummy BDT function that takes some time."""

    rand_value = random.random()

    if rand_value < 0.5:
    # List the OS servers
        for server in os_connection.compute.servers():
            print(server.to_dict())
    else:
        networks = os_connection.network.networks()
        
        for network in networks:
            print(network.to_dict())
    
    time.sleep(t)


if __name__ == '__main__':
    # Initialize and turn on debug logging
    # openstack.enable_logging(debug=True)
    # Initialize connection and pass the registry to the OPENSTACKSDK
    connection = openstack.connect(cloud="gx")

    # Start up the server to expose the metrics.
    # start_http_server(9000)
    # # Generate some requests.

    t_end = time.time() + 60 * BENCHMARK_DURATION_MINUTES
    while time.time() < t_end:
        process_bdt(connection, random.randrange(API_CALL_SLEEP_SECONDS_MIN, API_CALL_SLEEP_SECONDS_MAX))

    push_to_gateway(PROMETHEUS_URL, job=PROMETHEUS_JOB_NAME, registry=REGISTRY)
    write_to_textfile('./test.prom', REGISTRY)

    print("Finished running script")