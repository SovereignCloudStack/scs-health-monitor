from neutronclient.v2_0 import client as neutronclient
from environment_setup import before_all, after_all
import yaml
from behave import given, when, then
#
# def before_all(context):
#     before_all(context)
#
# def after_all(context):
#     after_all(context)
#

class StepsDef:

    @staticmethod
    def load_env_from_yaml():
        with open("env.yaml", 'r+') as file:
            env = yaml.safe_load(file)
        return env

    @given('I have the OpenStack environment variables set')
    def given_i_have_openstack_env_vars_set(context):
        context.env = StepsDef.load_env_from_yaml()

    @when('I connect to OpenStack')
    def when_i_connect_to_openstack(context):
        context.neutron = neutronclient.Client(
            auth_url=context.env["OS_AUTH_URL"],
            token=context.env["OS_APPLICATION_CREDENTIAL_ID"],
            token_secret=context.env["OS_APPLICATION_CREDENTIAL_SECRET"],
            project_name=context.env["OS_PROJECT_NAME"],
            user_domain_name=context.env["OS_USER_DOMAIN_NAME"],
            project_domain_name=context.env["OS_PROJECT_DOMAIN_NAME"]
        )

    @then('I should be able to list networks')
    def then_i_should_be_able_to_list_networks(context):
        networks = context.neutron.list_networks()["networks"]
        assert networks, "Failed to list networks. No networks found."
        for net in networks:
            print(f"- {net['name']} ({net['id']})")