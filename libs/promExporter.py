from prometheus_client import start_http_server, Counter, push_to_gateway, REGISTRY
import time
import logging
import json


# Initialize Prometheus counter for log events
log_counter = Counter('log_events_total', 'Total number of log events', ['level'])
passed_tests = Counter('behave_passed_tests', 'Number of passed Behave tests')
failed_tests = Counter('behave_failed_tests', 'Number of failed Behave tests')
pending_tests = Counter('behave_pending_tests', 'Number of pending Behave tests')


# Set up logging
logging.basicConfig(level=logging.INFO)
# Define a custom logging handler to increment Prometheus counter
class PrometheusLogHandler(logging.Handler):
    def emit(self, record):
        log_counter.labels(level=record.levelname).inc()
# Add PrometheusLogHandler to root logger
root_logger = logging.getLogger()
root_logger.addHandler(PrometheusLogHandler())


def update_metrics():
    while True:
        root_logger.info('This is an info message')
        root_logger.warning('This is a warning message') 
        parse_json_report('<path to repo>/scs-health-monitor/output/report.json')       
        push_to_gateway('http://localhost:3008', job='exporterTest', registry=REGISTRY)
        time.sleep(5)

def parse_json_report(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        # Extract relevant information from the JSON report
        passed_count = data.get('passed', 0)
        failed_count = data.get('failed', 0)
        pending_count = data.get('pending', 0)
        # Update Prometheus counters
        passed_tests.inc(passed_count)
        failed_tests.inc(failed_count)
        pending_tests.inc(pending_count)
        print(f"behave: passed {passed_count} failed {failed_count} pending {pending_count}")

if __name__ == '__main__':
    start_http_server(8000)
    update_metrics()

    