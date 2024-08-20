from prometheus_client import push_to_gateway, write_to_textfile, REGISTRY, CollectorRegistry, Metric
from prometheus_client.samples import Sample
from prometheus_client.registry import Collector
import re

class CommandTypes:
    API = "api-call"
    IPERF = "iperf3"
    SSH = "ssh"
    PING = "ping"

class LabelNames:
    COMMAND_LABEL = "command"
    CLOUD_LABEL = "cloud"
    RESOURCE_LABEL = "resource"
    ENDPOINT_URL = "endpoint"
    STATUS_CODE = "status_code"
    METHOD = "method"
 #   RESULT = "testresult"

class LabelValues:
    COMMAND_VALUE_IPERF3 = "iperf3"
    COMMAND_VALUE_TOT_DUR = "totDur"


# Class is intended to be used only internally for prometheus exporter
class CustomCollector(Collector):
    url_resource_pattern = r"(?:https?://)?[^/]+/v[^/]+/([^/]+)"

    def __init__(self, default_labels=None, excluded_labels=None):
        self.default_labels = default_labels or {}
        self.excluded_labels = excluded_labels or []

    def collect(self):
        """
            Collect and process metrics from the registry, applying label filtering, default labels, 
            and custom transformations for specific metrics.
            This function retrieves metrics from the registry, modifies them according to specified rules,
            and then yields the processed metrics.

            Returns:
                generator: A generator yielding processed `Metric` objects.

            Example:
                >>> for metric in instance.collect():
                ...     print(metric.name, metric.samples)
        """
        metrics = REGISTRY.collect()

        for metric in metrics:
            new_metric = Metric(metric.name, metric.documentation, metric.type, metric.unit)
            for sample in metric.samples:
                new_labels = {k: v for k, v in sample.labels.items() if k not in self.excluded_labels}
                new_sample = Sample(sample.name, new_labels, sample.value, sample.timestamp, sample.exemplar)
                
                for key, value in self.default_labels.items():
                    self.add_label(key, value, new_sample.labels)

                if LabelNames.STATUS_CODE in new_sample.labels and LabelNames.METHOD in new_sample.labels and LabelNames.ENDPOINT_URL in new_sample.labels:
                    self.add_label(LabelNames.COMMAND_LABEL, CommandTypes.API, new_sample.labels)

                url_value = new_sample.labels.get(LabelNames.ENDPOINT_URL, None)
                if url_value:                    
                    parsed_resource = self.parse_resource_from_metric(url_value)
                    self.add_label(LabelNames.RESOURCE_LABEL, parsed_resource, new_sample.labels)

                new_metric.samples.append(new_sample)
            yield new_metric

    def add_label(self, key, value, labels):
        """
            Add a label to a dictionary of labels if the label key is not already present 
            and is not in the list of excluded labels.

            Args:
                key (str): The label key to add.
                value (str): The value associated with the label key.
                labels (dict): The dictionary of labels to which the new label will be added.

            Example:
                >>> labels = {"status_code": "200"}
                >>> instance.add_label("service", "compute", labels)
                >>> print(labels)
                {"status_code": "200", "service": "compute"}
        """
        if not key or not value or not labels:
            return
        
        if key not in labels and key not in self.excluded_labels:
            labels[key] = value

    def parse_resource_from_metric(self, url: str):
        """
            Extract a resource identifier from a URL based on a predefined pattern.

            Args:
                url (str): The URL from which to extract the resource identifier.

            Returns:
                str or None: The extracted resource identifier if a match is found; otherwise, None.

            Example:
                >>> resource = instance.parse_resource_from_metric("https://api.example.com/resource/12345")
        """
        match = re.search(self.url_resource_pattern, url)    
        return match.group(1) if match else None

class PrometheusExporter: 
    """
    A class for exporting metrics to Prometheus, including functionality to add default labels, 
    push metrics to a gateway, and write metrics to a file.

    Attributes:
        registry (CollectorRegistry): The Prometheus collector registry.
        collector (CustomCollector): The custom collector instance used to gather metrics.
    """
    def __init__(self, default_labels=None, excluded_labels=None):
        """
        Initialize the PrometheusExporter with optional default and excluded labels.

        Args:
            default_labels (dict, optional): A dictionary of default labels to apply to all metrics.
            excluded_labels (list, optional): A list of label keys to exclude from the metrics.
        """
        self.registry = CollectorRegistry()
        self.collector = CustomCollector(default_labels, excluded_labels)
        self.registry.register(self.collector)

    def add_default_label(self, key, value):
        """
        Add or update a default label to be applied to all metrics.

        Args:
            key (str): The label key to add or update.
            value (str): The value associated with the label key.
        """
        self.collector.default_labels[key] = value

    def push_metrics(self, endpoint, job):
        """
        Push the collected metrics to a Prometheus push gateway.

        Args:
            endpoint (str): The URL of the Prometheus push gateway.
            job (str): The job name under which the metrics will be pushed.
        """
        push_to_gateway(endpoint, job=job, registry=self.registry)

    def write_metrics_to_file(self, pathToFile):
        """
        Write the collected metrics to a file in Prometheus text format.

        Args:
            pathToFile (str): The file path where the metrics will be written.
        """
        write_to_textfile(pathToFile, registry=self.registry)