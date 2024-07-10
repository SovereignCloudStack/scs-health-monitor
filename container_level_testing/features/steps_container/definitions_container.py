# import kubernetes.client
# from kubernetes.client.rest import ApiException
# from pprint import pprint
#
#
# configuration = kubernetes.client.Configuration()
#
# configuration.api_key['authorization'] = 'YOUR_API_KEY'
#
# # Defining host is optional and default to http://localhost
# configuration.host = env.get("")
#
# # Defining host is optional and default to http://localhost
# configuration.host = "http://localhost"
# # Enter a context with an instance of the API kubernetes.client
# with kubernetes.client.ApiClient(configuration) as api_client:
#     # Create an instance of the API class
#     api_instance = kubernetes.client.WellKnownApi(api_client)
#
#     try:
#         api_response = api_instance.get_service_account_issuer_open_id_configuration()
#         pprint(api_response)
#     except ApiException as e:
#         print("Exception when calling WellKnownApi->get_service_account_issuer_open_id_configuration: %s\n" % e)
#

from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

from kubernetes import client, config, watch

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

v1 = client.CoreV1Api()
count = 10
w = watch.Watch()
for event in w.stream(v1.list_namespace, _request_timeout=60):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    count -= 1
    if not count:
        w.stop()

print("Ended.")