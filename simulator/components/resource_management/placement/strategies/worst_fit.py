from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine
from simulator.components.resource_management.placement.misc import vms_ordering

def worst_fit(ordering=None):
    """ Worst-Fit heuristic (tries to allocate each VM inside the server that has the minimum load,
    and has resources to host the VM).
    For pragmatism purposes, we can define the way VMs are ordered. By default, we can
    select "Increasing" or "Decreasing". If we don't pass the ordering parameter, the function
    will define a placement for VMs based on the ordering provided by the input file.

    Parameters
    ==========
    ordering : String
        Ordering of VMs to be used by the Worst-Fit heuristic
    """

    # Ordering VMs before selecting the VM placement
    vms = vms_ordering(ordering=ordering)

    for vm in vms:
        # As the Worst-Fit heuristic consists of choosing the server with minimum
        # load that has resources to host the VM, we choose for sorting servers
        # according to their demand (ascending), and then we pick the first server
        # in that list with resources to host the VM
        servers = sorted(Server.all(), key=lambda sv:
            (sv.cpu_demand, sv.memory_demand, sv.disk_demand))

        for server in servers:
            if server.has_capacity_to_host(vm):

                server.virtual_machines.append(vm)

                server.cpu_demand += vm.cpu_demand
                server.memory_demand += vm.memory_demand
                server.disk_demand += vm.disk_demand

                vm.server = server

                break
