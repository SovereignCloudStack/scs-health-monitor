from prometheus_client import push_to_gateway, write_to_textfile, REGISTRY, CollectorRegistry, Metric
from prometheus_client.samples import Sample
from prometheus_client.registry import Collector
import re

class CommandTypes:
    API = "api-call"
    IPERF = "iperf"
    SSH = "ssh"

class LabelNames:
    COMMAND_LABEL = "command"
    CLOUD_LABEL = "cloud"
    RESOURCE_LABEL = "resource"
    ENDPOINT_URL = "endpoint"
    STATUS_CODE = "status_code"
    METHOD = "method"

# Class is intended to be used only internally for prometheus exporter
class CustomCollector(Collector):
    url_resource_pattern = r"(?:https?://)?[^/]+/v[^/]+/([^/]+)"

    def __init__(self, default_labels=None, excluded_labels=None):
        self.default_labels = default_labels or {}
        self.excluded_labels = excluded_labels or []

    # Iterate over all the gathered metrics and 
    # add default labels to them
    def collect(self):
        metrics = REGISTRY.collect()

        for metric in metrics:
            new_metric = Metric(metric.name, metric.documentation, metric.type, metric.unit)
            for sample in metric.samples:
                new_labels = {k: v for k, v in sample.labels.items() if k not in self.excluded_labels}
                new_sample = Sample(sample.name, new_labels, sample.value, sample.timestamp, sample.exemplar)
                
                for key, value in self.default_labels.items():
                    self.add_label(key, value, new_sample.labels)

                # Add command label if the metric contains labels status_code, method and endpoint 
                # This is intended for the metrics gathered from the openstack SDK
                if LabelNames.STATUS_CODE in new_sample.labels and LabelNames.METHOD in new_sample.labels and LabelNames.ENDPOINT_URL in new_sample.labels:
                    self.add_label(LabelNames.COMMAND_LABEL, CommandTypes.API, new_sample.labels)

                # Add resource label parsed from 'endpoint' label
                # This is intended for the metrics gathered from the openstack SDK
                url_value = new_sample.labels.get(LabelNames.ENDPOINT_URL, None)
                if url_value:                    
                    parsed_resource = self.parse_resource_from_metric(url_value)
                    self.add_label(LabelNames.RESOURCE_LABEL, parsed_resource, new_sample.labels)

                new_metric.samples.append(new_sample)
            yield new_metric

    def add_label(self, key, value, labels):
        if not key or not value or not labels:
            return
        
        if key not in labels and key not in self.excluded_labels:
            labels[key] = value

    def parse_resource_from_metric(self, url: str):
        match = re.search(self.url_resource_pattern, url)    
        return match.group(1) if match else None

class PrometheusExporter: 
    def __init__(self, default_labels=None, excluded_labels=None):
        self.registry = CollectorRegistry()
        self.collector = CustomCollector(default_labels, excluded_labels)
        self.registry.register(self.collector)

    def add_default_label(self, key, value):
        self.collector.default_labels[key] = value

    def push_metrics(self, endpoint, job):
        push_to_gateway(endpoint, job=job, registry=self.registry)

    def write_metrics_to_file(self, pathToFile):
        write_to_textfile(pathToFile, registry=self.registry)