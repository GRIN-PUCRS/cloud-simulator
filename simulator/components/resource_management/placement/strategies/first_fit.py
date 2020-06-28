from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine
from simulator.components.resource_management.placement.misc import vms_ordering

def first_fit(ordering=None):
    """ First-Fit heuristic (hosts each VM in the first server with enough resources).
    For pragmatism purposes, we can define the way VMs are ordered. By default, we can
    select "Increasing" or "Decreasing". If we don't pass the ordering parameter, the function
    will define a placement for VMs based on the ordering provided by the input file.

    Parameters
    ==========
    ordering : String
        Ordering of VMs to be used by the First-Fit heuristic
    """

    # Ordering VMs before selecting the VM placement
    vms = vms_ordering(ordering=ordering)

    for vm in vms:
        for server in Server.all():
            if server.has_capacity_to_host(vm):

                server.virtual_machines.append(vm)

                server.cpu_demand += vm.cpu_demand
                server.memory_demand += vm.memory_demand
                server.disk_demand += vm.disk_demand

                vm.server = server

                break
