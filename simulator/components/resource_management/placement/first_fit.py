from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine

def first_fit(ordering=None):
    """ First-Fit heuristic (hosts each VM in the first server with enough resources).
    For pragmatism purposes, we can define the way servers are ordered. By default, we can
    select "Increasing" or "Decreasing". If we don't pass the ordering parameter, the function
    will define a placement for VMs based on the ordering provided by the input file

    Parameters
    ==========
    ordering : String
        Ordering of servers to be used by the First-Fit heuristic
    """

    if ordering == 'Increasing':
        # Sorting servers by its demand (increasing)
        servers = sorted(Server.all(), key=lambda sv:
            (sv.cpu_capacity, sv.memory_capacity, sv.disk_capacity))

    elif ordering == 'Decreasing':
        # Sorting servers by its demand (increasing)
        servers = sorted(Server.all(), key=lambda sv:
            (sv.cpu_capacity, sv.memory_capacity, sv.disk_capacity))

    else:
        # Gathering all created servers with no explicit order
        servers = Server.all()


    for virtual_machine in VirtualMachine.all():
        for server in servers:
            # Selects the first server that has capacity to host the VM
            if server.has_capacity_to_host(virtual_machine):

                server.virtual_machines.append(virtual_machine)

                server.cpu_demand += virtual_machine.cpu_demand
                server.memory_demand += virtual_machine.memory_demand
                server.disk_demand += virtual_machine.disk_demand

                virtual_machine.server = server

                break
