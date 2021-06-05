# General-purpose simulator modules
from simulator.misc.simulation_environment import SimulationEnvironment
import simulator.misc.constants as constants

# Simulator Components
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine


def greedy_least_batch():
    """ Maintenance strategy proposed in [1]. It is designed to
    minimize the number of maintenance steps necessary to update
    the data center.

    References
    ==========
    [1] Zheng, Zeyu, et al. "Least maintenance batch scheduling in cloud
    data center networks." IEEE communications letters 18.6 (2014): 901-904.
    """

    # Patching servers nonupdated servers that are not hosting VMs
    servers_to_patch = Server.ready_to_patch()
    if len(servers_to_patch) > 0:
        servers_patch_duration = []

        for server in servers_to_patch:
            patch_duration = server.update()
            servers_patch_duration.append(patch_duration)

        # As servers are updated simultaneously, we don't need to call the function
        # that quantifies the server maintenance duration for each server being patched
        yield SimulationEnvironment.first().env.timeout(max(servers_patch_duration))


    # Migrating VMs
    else:
        servers_being_emptied = []

        # Sorts the servers to empty based on their occupation rate (ascending)
        servers_to_empty = sorted(Server.nonupdated(), key=lambda sv: sv.occupation_rate())

        for server in servers_to_empty:
            # We consider as candidate hosts for the VMs every server
            # not being emptied in the current iteration
            candidate_servers = [cand_server for cand_server in Server.all()
                if cand_server not in servers_being_emptied and cand_server != server]

            vms = [vm for vm in server.virtual_machines]

            if Server.can_host_vms(candidate_servers, vms):
                for _ in range(len(server.virtual_machines)):
                    vm = vms.pop(0)

                    # Sorting servers by update status (updated ones first) and demand (more occupied ones first)
                    candidate_servers = sorted(candidate_servers, key=lambda cand_server:
                        (-cand_server.updated, -cand_server.occupation_rate()))

                    # Using a First-Fit strategy to select a candidate host for each VM
                    for cand_server in candidate_servers:
                        if cand_server.has_capacity_to_host(vm):
                            yield SimulationEnvironment.first().env.timeout(vm.migrate(cand_server))
                            break

            if len(server.virtual_machines) == 0:
                servers_being_emptied.append(server)
