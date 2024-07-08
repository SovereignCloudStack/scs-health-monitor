from prometheus_client import push_to_gateway, REGISTRY
from steps.tools import Tools, Collector, delete_all_test_resources
from libs.loggerClass import Logger
from libs.PrometheusExporter import PrometheusExporter, LabelNames
from libs.DateTimeProvider import DateTimeProvider
from libs.Formatter import Formatter
from behave import fixture, use_fixture



import openstack

DEFAULT_PROMETHEUS_BATCH_NAME = "SCS-Health-Monitor"
DEFAULT_CLOUD_NAME = "gx"
DEFAULT_LOG_LEVEL = "INFO"


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
    context.start_time = DateTimeProvider.get_current_utc_time()

    setup_class = SetupClass()
    setup_class.setup()
    context.env = Tools.load_env_from_yaml()
    cloudName = context.env.get("CLOUD_NAME", DEFAULT_CLOUD_NAME)

    context.logger = Logger(level=DEFAULT_LOG_LEVEL)
    context.prometheusExporter = PrometheusExporter()
    context.prometheusExporter.add_default_label(LabelNames.CLOUD_LABEL, cloudName)

    context.collector = Collector()


def after_feature(context, feature):
    """
        behave framework hook: code will run after each feature
        checks if the feature has failed and if it belongs to the creational or deletional features
        then it would perform a cleanup
        
        Args:
            context(object): context
            feature: current feature

        Returns:
            call for cleanup
    """
    feature_failed = any(scenario.status == 'failed' for scenario in feature.scenarios)
    context.logger.log_info(f"feature tag {feature.tags}")
    if feature_failed:
        context.logger.log_info(f"Feature '{feature.name}' failed: performing cleanup or additional actions")
        if "create" in feature.tags or "delete" in feature.tag:
            if context.collector:
                context.logger.log_info(f"Feature '{feature.name}' is a deletion or creation feature: performing cleanup")
                cloud_name = context.env.get("CLOUD_NAME")
                context.client = openstack.connect(cloud=cloud_name)
                delete_all_test_resources(context) 
    else:
        context.logger.log_info(f"Feature '{feature.name}' passed")
    context.logger.log_info(f"Feature completed: performing additional actions")
    if context.collector:
        context.logger.log_info(f"this is in the collector {context.collector}")


def after_all(context):
    context.stop_time = DateTimeProvider.get_current_utc_time()
    
    if context.collector:
        cloud_name = context.env.get("CLOUD_NAME")
        context.client = openstack.connect(cloud=cloud_name)
        delete_all_test_resources(context)

    formattedDuration = f"from_{Formatter.format_date_time(context.start_time)}_to_{Formatter.format_date_time(context.stop_time)}"
    teardown_class = TeardownClass()
    teardown_class.teardown()
    prometheus_endpoint = context.env.get("PROMETHEUS_ENDPOINT", "")
    prometheus_batch_name = context.env.get("PROMETHEUS_BATCH_NAME", DEFAULT_PROMETHEUS_BATCH_NAME)

    append_timestamp_to_batch_name = Tools.env_is_true(context.env.get("APPEND_TIMESTAMP_TO_BATCH_NAME", True))

    if append_timestamp_to_batch_name and prometheus_batch_name:
        prometheus_batch_name = f"{prometheus_batch_name}_{formattedDuration}"

    if prometheus_endpoint:
        context.prometheusExporter.push_metrics(prometheus_endpoint, prometheus_batch_name)
    else:
        context.logger.log_warning(
            "PROMETHEUS_ENDPOINT environment variables is not set. Metrics not pushed to prometheus push gateway.")
