from environment_setup import before_all, after_all
import yaml
from behave import given, when, then
import openstack

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

    @when('A network with name {network_name} exists')
    def when_i_connect_to_openstack(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"

    @then('I should be able to list networks')
    def then_i_should_be_able_to_list_networks(context):
        networks = context.client.network.networks()
        assert networks, "Failed to list networks. No networks found."

    @then('I should be able to create a network with name {network_name}')
    def then_i_should_be_able_to_create_a_network(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is None, f"Network with {network_name} already exists"
        context.client.network.create_network(name=network_name)

    @then('I should be able to delete a network with name {network_name}')
    def then_i_should_be_able_to_delete_a_network(context, network_name: str):
        network = context.client.network.find_network(name_or_id=network_name)
        assert network is not None, f"Network with {network_name} doesn't exists"
        context.client.network.delete_network(network)
        assert not context.client.network.find_network(name_or_id=network), f"Network called {network_name} already deleted"
