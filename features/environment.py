from prometheus_client import push_to_gateway, REGISTRY
from steps.tools import Tools
from libs.loggerClass import Logger

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
    print("Running before all")
    
    setup_class = SetupClass()
    setup_class.setup()
    context.env = Tools.load_env_from_yaml()

    context.logger = Logger();

    #TODO add logger to context

def after_all(context):
    teardown_class = TeardownClass()
    teardown_class.teardown()
    prometheus_endpoint = context.env.get("PROMETHEUS_ENDPOINT", "")
    prometheus_batch_name = context.env.get("PROMETHEUS_BATCH_NAME", DEFAULT_PROMETHEUS_BATCH_NAME)
    
    if prometheus_endpoint:
        push_to_gateway(prometheus_endpoint, job=prometheus_batch_name, registry=REGISTRY)
    else:
        context.logger.logWarning("PROMETHEUS_ENDPOINT environment variables is not set. Metrics not pushed to prometheus push gateway.")
    
    


