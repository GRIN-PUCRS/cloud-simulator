# General-purpose simulator modules
from simulator.misc.simulation_environment import SimulationEnvironment
import simulator.misc.constants as constants

# Simulator Components
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine


def best_fit_like():
    """
    Best-Fit-like maintenance strategy (presented by Severo et al.)
    ====================================================================
    Note: We use the term "empty" to refer to servers that are not hosting VMs.

    The maintenance process is divided in two tasks:
    (i) Patching empty servers (lines 25-35)
    (ii) Migrating VMs to empty more servers (lines 40-72)

    When choosing which servers will host the VMs, this
    strategy uses the Best-Fit Decreasing heuristic.
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


    # (ii) Migrating VMs to empty more servers
    else:
        servers_being_emptied = []

        # Getting the list of servers that still need to receive the patch
        servers_to_empty = Server.nonupdated()

        for server in servers_to_empty:
            # We consider as candidate hosts for the VMs all Server
            # objects not being emptied in the current maintenance step
            candidate_servers = [cand_server for cand_server in Server.all()
                if cand_server not in servers_being_emptied and cand_server != server]

            
            # Sorting VMs by its demand (decreasing)
            vms = [vm for vm in server.virtual_machines]
            vms = sorted(vms, key=lambda vm: -vm.demand())

            for _ in range(len(server.virtual_machines)):
                vm = vms.pop(0)

                # Sorting servers (bins) to align with Best-Fit's idea,
                # which is prioritizing servers with less space remaining
                candidate_servers = sorted(candidate_servers,
                    key=lambda cand: -cand.occupation_rate())

                # Migrating VMs using the Best-Fit heuristic
                for cand_server in candidate_servers:
                    if cand_server.has_capacity_to_host(vm):
                        # Migrating the VM and storing the migration duration to allow future analysis
                        yield SimulationEnvironment.first().env.timeout(vm.migrate(cand_server))
                        break

            if len(server.virtual_machines) == 0:
                servers_being_emptied.append(server)
