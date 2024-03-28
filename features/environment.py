from prometheus_client import push_to_gateway, REGISTRY
from steps.tools import Tools
from libs.loggerClass import Logger
from libs.PrometheusExporter import PrometheusExporter, LabelNames
from libs.DateTimeProvider import DateTimeProvider
from libs.Formatter import Formatter

DEFAULT_PROMETHEUS_BATCH_NAME = "SCS-Health-Monitor"

class SetupClass:
    def __init__(self):
        pass

    def setup(self):
        # Your setup logic here
        pass

class TeardownClass:
    def __init__(self):
        pass

    def teardown(self):
        # Your teardown logic here
        pass

def before_all(context):
    setup_class = SetupClass()
    setup_class.setup()
    context.env = Tools.load_env_from_yaml()
    cloudName = context.env.get("CLOUD_NAME", "gx")

    context.logger = Logger()
    context.prometheusExporter = PrometheusExporter()
    context.prometheusExporter.add_default_label(LabelNames.CLOUD_LABEL, cloudName)

def after_all(context):
    teardown_class = TeardownClass()
    teardown_class.teardown()
    prometheus_endpoint = context.env.get("PROMETHEUS_ENDPOINT", "")
    prometheus_batch_name = context.env.get("PROMETHEUS_BATCH_NAME", DEFAULT_PROMETHEUS_BATCH_NAME)
    
    if prometheus_endpoint:
        context.prometheusExporter.push_metrics(prometheus_endpoint, prometheus_batch_name)
    else:
        context.logger.log_warning("PROMETHEUS_ENDPOINT environment variables is not set. Metrics not pushed to prometheus push gateway.")
    
    


