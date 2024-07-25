def create_lb(client, name, **kwargs):
    """
    Create Loadbalancer and wait until it's in state active
    @param client: OpenStack client
    @param name: lb name
    @param kwargs: Arguments to be passed to creation command
    """
    print(kwargs)
    assert (client.load_balancer.create_load_balancer(name=name, **kwargs).
            provisioning_status == "PENDING_CREATE"), f"Expected LB {name} not in creation"
    lb = client.load_balancer.wait_for_load_balancer(name_or_id=name,
                                                     status='ACTIVE',
                                                     failures=['ERROR'], interval=2,
                                                     wait=300)
    assert lb.provisioning_status == "ACTIVE", f"Expected LB {name} not Active"
    assert lb.operating_status == "ONLINE", f"Expected LB {name} not Online"
    return lb
