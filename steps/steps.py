from environment_setup import before_all, after_all
import yaml
from behave import given, when, then
import openstack
from openstack.config import loader
import time

def before_all(context):
    before_all(context)

def after_all(context):
    after_all(context)


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
        context.client = openstack.connect(cloud="gx")


    @then('I should be able to list networks')
    def then_i_should_be_able_to_list_networks(context):
        networks = context.client.network.networks()
        assert networks, "Failed to list networks. No networks found."
        for net in networks:
            print(f"- {net['name']} ({net['id']})")
