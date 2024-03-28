from prometheus_client import push_to_gateway, write_to_textfile, REGISTRY, CollectorRegistry, Metric
from prometheus_client.samples import Sample
from prometheus_client.registry import Collector

class CommandTypes:
    API = "api-call"
    IPERF = "iperf"
    SSH = "ssh"

class LabelNames:
    COMMAND_LABEL = "command"
    CLOUD_LABEL = "cloud"

# Class is intended to be used only internally for prometheus exporter
class CustomCollector(Collector):
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
                    if key not in new_sample.labels and key not in self.excluded_labels:
                        new_sample.labels[key] = value

                # Add command label if the metric contains labels status_code, method and endpoint 
                # This is intended for the metrics gathered from the openstack SDK
                if 'status_code' in new_sample.labels and 'method' in new_sample.labels and 'endpoint' in new_sample.labels:
                    if LabelNames.COMMAND_LABEL not in new_sample.labels and LabelNames.COMMAND_LABEL not in self.excluded_labels:
                        new_sample.labels[LabelNames.COMMAND_LABEL] = CommandTypes.API

                new_metric.samples.append(new_sample)
            yield new_metric

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