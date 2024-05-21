from prometheus_client import push_to_gateway, REGISTRY
from steps.tools import Tools, Collector
from libs.loggerClass import Logger
from libs.PrometheusExporter import PrometheusExporter, LabelNames
from libs.DateTimeProvider import DateTimeProvider
from libs.Formatter import Formatter

DEFAULT_PROMETHEUS_BATCH_NAME = "SCS-Health-Monitor"
DEFAULT_CLOUD_NAME = "gx"
DEFAULT_LOG_LEVEL = "DEBUG"


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


def after_all(context):
    context.stop_time = DateTimeProvider.get_current_utc_time()

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
