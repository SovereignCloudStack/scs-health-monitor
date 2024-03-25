# OpenStack metrics

The following documentation outlines the metrics exposed by a Prometheus gateway in the context of an OpenStack service monitoring environment. 

These metrics, designed to be scraped by Prometheus, offer valuable insights into the performance and behavior of the OpenStack services. As the nature of the test cases is short-lived, these metrics are initially pushed to a Prometheus Pushgateway and then pulled by Prometheus for analysis. 

Each metric is described in detail, including its type, purpose, associated labels, and examples, to facilitate effective monitoring and analysis of the OpenStack infrastructure.

These metrics are exposed by the OpenStack python SDK by default.

## Metrics in prometheus
Each type of metric serves a different purpose and is suited to different types of data. Understanding the types of metrics helps in interpreting and using the data collected by Prometheus effectively for monitoring and analysis. Here are the common types of metrics that can be stored in prometheus:

1) **Counter:**
   - **Definition**: A counter is a cumulative metric that represents a single monotonically increasing value. Counters cannot be decreased; they can only be reset to zero.
   - **Use Case**: Counters are typically used to represent values that continuously increase over time, such as the total number of events or occurrences of a particular event.
   - **Example**: openstack_http_requests_total

2) **Gauge:**
   - **Definition**: A gauge is a metric that represents a single numerical value that can arbitrarily go up and down.
   - **Use Case**: Gauges are used for measured values that can change freely, such as the current temperature, memory usage, or the number of active threads.
   - **Example**: openstack_http_requests_created

3) **Histogram:**
   - **Definition**: A histogram samples observations (usually durations or sizes) and counts them in configurable buckets. It also provides a sum of all observed values.
   - **Use Case**: Histograms are useful for understanding the distribution of values within a dataset. They are commonly used for measuring response times, request sizes, or any other latency or size-related metric.
   - **Example**: openstack_http_response_time

4) **Summary:**
   - **Definition**: Similar to histograms, summaries also sample observations and provide a configurable quantile. However, unlike histograms, they do not provide quantile buckets.
   - **Use Case**: Summaries are suitable for scenarios where quantiles need to be calculated on the client side. They are often used for monitoring latency distributions.
   - **Example**: Not present in the exposed metrics.

More information on prometheus metrics can be found [here](https://prometheus.io/docs/concepts/metric_types/).

## Exposed metrics by OpenStack SDK

### openstack_http_requests_created:
- **Type:** Gauge
- **Description:** Number of HTTP requests made to an OpenStack service.
- **Labels:**
  - endpoint: The endpoint URL of the OpenStack service.
  - method: The HTTP method used (e.g., GET).
  - service_type: The type of service (e.g., network).
  - status_code: The HTTP status code of the response.
  - job: The name of the job.
- **Example:** `openstack_http_requests_created{endpoint="https://api.gx-scs.sovereignit.cloud:9696/v2.0/networks", method="GET", service_type="network", status_code="200"}`

### openstack_http_requests_total:
- **Type:** Counter
- **Description:** Number of total HTTP requests made to an OpenStack service.
- **Labels:**
  - endpoint: The endpoint URL of the OpenStack service.
  - method: The HTTP method used (e.g., GET).
  - service_type: The type of service (e.g., network).
  - status_code: The HTTP status code of the response.
  - job: The name of the job.
- **Example:** `
openstack_http_requests_total{endpoint="https://api.gx-scs.sovereignit.cloud:9696/v2.0/networks", method="GET", service_type="network", status_code="200"}
`


### openstack_http_response_time:
- **Type:** Histogram
- **Description:** Time taken for an HTTP response to an OpenStack service.
- **Labels:**
  - endpoint: The endpoint URL of the OpenStack service.
  - method: The HTTP method used (e.g., GET).
  - service_type: The type of service (e.g., network).
  - status_code: The HTTP status code of the response.
  - le: Time bucket (less than or equal to).
  - job: The name of the job.
- **Example:** `openstack_http_response_time_bucket{endpoint="https://api.gx-scs.sovereignit.cloud:9696/v2.0/networks", method="GET", service_type="network", status_code="200", le="0.005"}`

### openstack_http_response_time_created:
- **Type:** Gauge
- **Description:** Time taken for an HTTP response to an OpenStack service (creation time).
- **Labels:**
  - endpoint: The endpoint URL of the OpenStack service.
  - method: The HTTP method used (e.g., GET).
  - service_type: The type of service (e.g., network).
  - status_code: The HTTP status code of the response.
  - job: The name of the job.
- **Example:** `openstack_http_response_time_created{endpoint="https://api.gx-scs.sovereignit.cloud:9696/v2.0/networks", method="GET", service_type="network", status_code="200"}`

### push_failure_time_seconds:
- **Type:** Gauge
- **Description:** Last Unix time when changing this group in the Pushgateway failed.
- **Labels:**
  - job: The name of the job.
- **Example:** `push_failure_time_seconds{job="SCS-Health-Monitor"}`

### push_time_seconds:
- **Type:** Gauge
- **Description:** Last Unix time when changing this group in the Pushgateway succeeded.
- **Labels:**
  - job: The name of the job.
- **Example:** `push_time_seconds{job="SCS-Health-Monitor"}`

### python_gc_collections_total:
- **Type:** Counter
- **Description:** Number of times each generation was collected during garbage collection.
- **Labels:**
  - generation: The generation of garbage collection (0, 1, or 2).
  - job: The name of the job.
- **Example:** `python_gc_collections_total{generation="0"}`

### python_gc_objects_collected_total:
- **Type:** Counter
- **Description:** Number of objects collected during garbage collection for each generation.
- **Labels:**
  - generation: The generation of garbage collection (0, 1, or 2).
  - job: The name of the job.
- **Example:** `python_gc_objects_collected_total{generation="0"}`

### python_gc_objects_uncollectable_total:
- **Type:** Counter
- **Description:** Number of uncollectable objects found during garbage collection for each generation.
- **Labels:**
  - generation: The generation of garbage collection (0, 1, or 2).
  - job: The name of the job.
- **Example:** `python_gc_objects_uncollectable_total{generation="0"}`

### python_info:
- **Type:** Gauge
- **Description:** Python platform information.
- **Labels:**
  - implementation: The Python implementation (e.g., CPython).
  - major: Major version of Python.
  - minor
  - job: The name of the job.
- **Example:** `python_info{implementation="CPython",instance="",job="SCS-Health-Monitor",major="3",minor="10",patchlevel="11",version="3.10.11"} 1`


