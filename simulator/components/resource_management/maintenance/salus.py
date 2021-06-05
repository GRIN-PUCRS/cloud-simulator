# General-purpose simulator modules
from simulator.misc.simulation_environment import SimulationEnvironment
import simulator.misc.constants as constants

# Simulator Components
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine


def salus():
    """ Salus is the Roman goddess of safety. This maintenance
    strategy was proposed by Severo et al. in 2020.
    
    Note: We use the term "empty" to refer to servers that are not hosting VMs

    When choosing which servers to empty, this heuristic prioritizes servers with
    a smaller update cost, which takes into account multiple factors such as server
    capacity and server's patch duration.

    The maintenance process is divided in two tasks:
    (i) Patching empty servers (lines 28-36)
    (ii) Migrating VMs to empty more servers (lines 41-74)
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

        # Sorts the servers to empty based on its update score. This score considers the amount of time
        # needed to update the server (including VM migrations to draining the server) and its capacity
        servers_to_empty = sorted(Server.nonupdated(), key=lambda sv:
            (sv.maintenance_duration() * (1/(sv.capacity()+1))) ** (1/2))


        for server in servers_to_empty:
            # We consider as candidate hosts for the VMs all Server
            # objects not being emptied in the current maintenance step
            candidate_servers = [cand_server for cand_server in Server.all()
                if cand_server not in servers_being_emptied and cand_server != server]

            # Sorting VMs by its demand (decreasing)
            vms = [vm for vm in server.virtual_machines]
            vms = sorted(vms, key=lambda vm: -vm.demand())

            if Server.can_host_vms(candidate_servers, vms):
                for _ in range(len(server.virtual_machines)):
                    vm = vms.pop(0)

                    # Sorting servers by update status (updated ones first) and demand (decreasing)
                    candidate_servers = sorted(candidate_servers, key=lambda sv:
                        (-sv.updated, -sv.occupation_rate()))

                    # Using a Best-Fit Decreasing strategy to select a candidate host for each VM
                    for cand_server in candidate_servers:
                        if cand_server.has_capacity_to_host(vm):
                            yield SimulationEnvironment.first().env.timeout(vm.migrate(cand_server))
                            break

            if len(server.virtual_machines) == 0:
                servers_being_emptied.append(server)
