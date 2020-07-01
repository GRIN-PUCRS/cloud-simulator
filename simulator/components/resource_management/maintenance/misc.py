import csv

from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine

def server_update(env, patching_time):
    """ Quantifies the number of simulation steps used to update a server.

    Parameters
    ==========
    env : SimPy.Environment
        Used to quantity the amount of simulation time spent by the migration

    patching_time : Integer
        Defines the amount of time it takes to patch a server
    """

    yield env.timeout(patching_time)

def collect_metrics(env, strategy, servers_patched, servers_being_emptied, migrations_data):
    """ Gather metrics from the current maintenance step.

    Supported metrics:
        - Simulation steps
        - Number of servers being updated
        - Number of servers being emptied
        - Number of updated servers
        - Number of nonupdated servers
        - Vulnerability Surface (Severo et al. 2020)
        - Number of VM migrations
        - Overall migrations duration (amount of time spent with migrations in the current step)
        - Longer migration
        - Shorter migration
        - Average migration duration
        - Servers occupation rate
        - Servers consolidation rate

    Parameters
    ==========
    env : SimPy.Environment
        Used to quantity the amount of simulation time spent by the migration

    strategy : String
        Name of the used maintenance strategy

    servers_patched : List
        List of servers updated in the current maintenance step

    servers_being_emptied : List
        List of servers being emptied in the current maintenance step

    migrations_data : List
        Information on each migration performed in the current maintenance step

    Returns
    =======
    output : Dictionary
        List of metrics collected during the current maintenance step
    """

    output = {}

    # Number of simulation steps
    output['simulation_steps'] = env.now

    # Name of the used maintenance strategy
    output['strategy'] = strategy

    # Other simulation metrics
    output['metrics'] = {}

    # Number of updated and nonupdated servers
    output['metrics']['updated_servers'] = len(Server.updated())
    output['metrics']['nonupdated_servers'] = len(Server.nonupdated())

    # Vulnerability Surface (Severo et al. 2020) = Number of non-updated servers * Elapsed time
    output['metrics']['vulnerability_surface'] = env.now * output['metrics']['nonupdated_servers']

    # Gathering VM migration metrics
    output['metrics']['vm_migrations'] = 0
    output['metrics']['migrations_duration'] = 0
    output['metrics']['longer_migration'] = 0
    output['metrics']['shorter_migration'] = 0
    output['metrics']['avg_migration_duration'] = 0

    if len(migrations_data) > 0:
        # Number of VM migrations performed in this interval
        output['metrics']['vm_migrations'] = len(migrations_data)

        # Time spent performing VM migrations
        migrations_duration = sum(migr['duration'] for migr in migrations_data)
        output['metrics']['migrations_duration'] = migrations_duration

        # Longer migration
        output['metrics']['longer_migration'] = max(migr['duration'] for migr in migrations_data)

        # Shorter migration
        output['metrics']['shorter_migration'] = min(migr['duration'] for migr in migrations_data)

        # Average migration duration
        output['metrics']['avg_migration_duration'] = migrations_duration / len(migrations_data)

    # Gathering server-related metrics
    # Occupation rate
    aggregated_occupation_rate = sum(sv.occupation_rate() for sv in Server.all())
    output['metrics']['occupation_rate'] = aggregated_occupation_rate / len(Server.used_servers())

    # Consolidation rate
    output['metrics']['consolidation_rate'] = Server.consolidation_rate()

    # Servers being updated
    output['metrics']['servers_being_updated'] = len(servers_patched)
    # Servers being emptied
    output['metrics']['servers_being_emptied'] = len(servers_being_emptied)

    return(output)

def show_metrics(dataset, maintenance_data, output_file=None, verbose=False):
    """ Presents information and metrics of the performed maintenance
    and optionally stores these results into an output CSV file.

    Parameters
    ==========
    dataset : String
        Name of the used dataset

    maintenance_data : Dictionary
        List of metrics collected during the current maintenance step

    output_file : String
        Optional parameters regarding the name of the output CSV file
    """

    # More generalistic metrics that collect data from each maintenance iteration
    vulnerability_surface_metric = 0
    total_vm_migrations = 0

    time_spent_with_migrations = 0
    avg_consolidation_rate = 0
    avg_occupation_rate = 0

    print('========================\n== SIMULATION RESULTS ==\n========================')

    # Printing out the name of the maintenance strategy
    print(f'Dataset: "{dataset}"')
    print(f'Maintenance Strategy: {maintenance_data[0]["strategy"]}\n')

    # Walking through each maintenance iteration
    for i, output in enumerate(maintenance_data):

        # Only shows specific information of each maintenance
        # iteration if the verbose flag is set to true
        if verbose == True:
            print(f'\n\n=== Iteration {i+1}. Passed Simulation Time: {output["simulation_steps"]} ===')

            if i > 0:
                iter_duration = output["simulation_steps"] - maintenance_data[i-1]["simulation_steps"]
                print(f'Duration: {iter_duration}')
            else:
                iter_duration = output["simulation_steps"]
                print(f'Duration: {iter_duration}')


            print(f'Updated Servers: {output["metrics"]["updated_servers"]}')
            print(f'Non-Updated Servers: {output["metrics"]["nonupdated_servers"]}\n')


            print(f'Servers updated: {output["metrics"]["servers_being_updated"]}')
            print(f'Servers emptied: {output["metrics"]["servers_being_emptied"]}\n')
            
            print(f'Occupation Rate: {output["metrics"]["occupation_rate"]}')
            print(f'Consolidation Rate: {output["metrics"]["consolidation_rate"]}\n')

            print(f'Migrations: {output["metrics"]["vm_migrations"]}')
            if output["metrics"]["vm_migrations"] > 0:
                print(f'   Time spent with migrations: {output["metrics"]["migrations_duration"]}')
                print(f'   Average migration duration: {output["metrics"]["avg_migration_duration"]}')
                print(f'   Longer migration: {output["metrics"]["longer_migration"]}')
                print(f'   Shorter migration: {output["metrics"]["shorter_migration"]}\n')

            print(f'Vulnerability Surface in this step: {output["metrics"]["vulnerability_surface"]}')

        # Updating generalistic variables with data from the current maintenance step
        time_spent_with_migrations += output["metrics"]["migrations_duration"]
        avg_occupation_rate += output["metrics"]["occupation_rate"]
        avg_consolidation_rate += output["metrics"]["consolidation_rate"]

        total_vm_migrations += output["metrics"]["vm_migrations"]
        vulnerability_surface_metric += output["metrics"]["vulnerability_surface"]

    avg_migration_duration = time_spent_with_migrations / total_vm_migrations
    avg_occupation_rate /= len(maintenance_data)
    avg_consolidation_rate /= len(maintenance_data)

    print('\n=========')
    print(f'Maintenance Duration: {maintenance_data[-1]["simulation_steps"]}')
    print(f'Overall Vulnerability Surface: {vulnerability_surface_metric}')
    print(f'VM Migrations: {total_vm_migrations}')
    print(f'Time Spent with Migrations: {time_spent_with_migrations}')
    print(f'Avg. Migration Duration: {avg_migration_duration}')
    print(f'Avg. Occupation Rate: {avg_occupation_rate}')
    print(f'Avg. Consolidation Rate: {avg_consolidation_rate}')

    # If the output_file parameter was provided, stores the maintenance results into a CSV file
    if output_file:

        with open(output_file, mode='w') as csv_file:
            output_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # Creating header
            output_writer.writerow(['Dataset', 'Strategy', 'Maintenance Duration',
                'Overall Vulnerability Surface', 'VM Migrations', 'Time Spent With Migrations',
                'Avg. Migration Duration', 'Avg. Occupation Rate', 'Avg. Consolidation Rate'])

            # Creating body
            output_writer.writerow([dataset, maintenance_data[0]["strategy"], maintenance_data[-1]["simulation_steps"],
                vulnerability_surface_metric, total_vm_migrations, time_spent_with_migrations,
                avg_migration_duration, avg_occupation_rate, avg_consolidation_rate])
