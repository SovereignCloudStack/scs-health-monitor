from behave import given, then

from definitions import StepsDef
import libs.static
import tools


class LbStepsDef(StepsDef):
    @given("I want to test loadbalancers")
    def test_lbs(context):
        context.test_name = f"{libs.static.get_tests_name_identification(context, '-lb-')}"

    @then("I should be able to create a network for each availability zone")
    def create_lb_networks(context):
        azs = list(tools.get_availability_zones(context.client))
        assert len(azs) > 0, "Assuming there are availability zones!"
        for az in azs:
            net = tools.create_network(context.client, f"{context.test_name}{az.name}")
            # TODO: continue!

    @then("I should be able to create {quantity} VMs for the LBs")
    def create_lb_vms(context, quantity):
        for num in range(0, int(quantity)):
            vm_name = f"{context.test_name}{num}"
            # TODO: Create networks!
            network = None
            tools.create_vm(context.client, vm_name, context.vm_image, context.flavor_name, network)

    @then("I should be able to create a loadbalancer")
    # TODO: Remove composit, and move to individual functions
    #  We test all functionality in this method first, before moving it to different ones
    #  Here we create all required LB components.
    #  TODO: Finish this by spawning Jump Host and VMs. We want to access web services on the VMs via the JH.
    def create_lb_combat(context):
        lb_name = context.test_name
        tools.create_lb(context.client, name=lb_name, vip_subnet_id="02390af9-7213-46d5-82b8-36af3734406e")
        lb_id = "f9963732-1858-4215-9553-8831d162f852"
        context.client.load_balancer.create_listener(name="listener", protocol="HTTP",
                                                  protocol_port=80, load_balancer_id=lb_id)
        pool_name = "pool"
        context.client.load_balancer.create_pool(name=pool_name,
                                              protocol="HTTP",
                                              lb_algorithm="ROUND_ROBIN",
                                              loadbalancer_id=lb_id)
        pool_id = "8d01205d-d367-4018-ab35-124494ed6258"
        # TODO: Access VM address
        context.client.load_balancer.create_member(pool_id, name="member-1", subnet="scs-hm-subnet-1",
                                                address="10.30.40.139", protocol_port=80)
