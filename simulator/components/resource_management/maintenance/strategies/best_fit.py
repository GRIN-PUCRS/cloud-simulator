from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine
from simulator.components.resource_management.maintenance.misc import server_update, collect_metrics
import simulator.misc.constants as constants

def best_fit(env, maintenance_data):
    """
    Best-Fit like maintenance strategy (presented by Severo et al. 2020)
    ====================================================================
    Note: We use the term "empty" to refer to servers that are not hosting VMs.

    The maintenance process is divided in two tasks:
    (i) Patching empty servers (lines 29-36)
    (ii) Migrating VMs to empty more servers (lines 40-77)

    When choosing which servers will host the VMs, this strategy uses the Best-Fit heuristic.

    Parameters
    ==========
    env : SimPy.Environment
        Used to quantity the amount of simulation time spent by the migration

    maintenance_data : List
        Object that will be filled during the maintenance, storing metrics on each maintenance step
    """

    while len(Server.nonupdated()) > 0:
        # (i) Patching servers nonupdated servers that are not hosting VMs (lines 30-37)
        servers_to_patch = Server.ready_to_patch()
        if len(servers_to_patch) > 0:
            for server in servers_to_patch:
                server.updated = True

            # As servers are updated simultaneously, we don't need to call the function
            # that quantifies the server maintenance duration for each server being patched
            yield env.process(server_update(env, constants.PATCHING_TIME))

        # (ii) Migrating VMs to empty more servers (lines 41-72)

        servers_being_emptied = []

        # Getting the list of servers that still need to receive the patch
        servers_to_empty = Server.nonupdated()
        migrations_data = [] # Stores data on the migrations performed to allow future analysis

        for server in servers_to_empty:

            candidate_servers = [cand_server for cand_server in Server.all()
                if cand_server != server and cand_server not in servers_being_emptied]

            vms_to_migrate = len(server.virtual_machines)
            servers_checked = 0

            while len(server.virtual_machines) > 0 and servers_checked <= vms_to_migrate * len(candidate_servers):

                vm = server.virtual_machines[0]

                # Sorting servers (bins) to align with Best-Fit's idea,
                # which is prioritizing servers with less space remaining
                candidate_servers = sorted(candidate_servers,
                    key=lambda cand: (-cand.cpu_demand, -cand.memory_demand, -cand.disk_demand))

                # Migrating VMs using the Worst-Fit heuristic
                for cand_server in candidate_servers:
                    servers_checked += 1
                    if cand_server.has_capacity_to_host(vm):

                        # Migrating the VM and storing the migration duration to allow future analysis
                        migration_duration = yield env.process(vm.migrate(env, cand_server))

                        migrations_data.append({ 'origin': server, 'destination': cand_server,
                            'vm': vm, 'duration': migration_duration })

                        break

            if len(server.virtual_machines) == 0:
                servers_being_emptied.append(server)

        # Collecting metrics gathered in the current maintenance iteration (i.e., outer while loop iteration)
        maintenance_data.append(collect_metrics(env, 'Best-Fit', servers_to_patch,
            servers_being_emptied, migrations_data))
