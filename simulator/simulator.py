# Python Libraries
import simpy
import json
import fnss
import networkx as nx
import pandas as pd

# General-purpose simulator modules
from simulator.misc.simulation_environment import SimulationEnvironment

# Simulator components
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine
from simulator.components.communication.fat_tree import FatTree

# Data center maintenance strategies
from simulator.components.resource_management.maintenance.best_fit_like import best_fit_like
from simulator.components.resource_management.maintenance.first_fit_like import first_fit_like
from simulator.components.resource_management.maintenance.worst_fit_like import worst_fit_like
from simulator.components.resource_management.maintenance.greedy_least_batch import greedy_least_batch
from simulator.components.resource_management.maintenance.salus import salus


# Auxiliary variable that defines whether the
# Simulator will print CSV-formatted results or not
CSV_READY_OUTPUT = False

class Simulator:
    """ This class allows the creation objects that
    control the whole life cycle of simulations.
    """

    environment = None


    @classmethod
    def create_environment(cls, simulation_type='normal'):
        """ Creates the simulation environment.
        """

        # Creating SimPy environment
        if simulation_type == 'normal':
            Simulator.environment = SimulationEnvironment(simulation_type='normal')
        elif simulation_type == 'real_time':
            Simulator.environment = SimulationEnvironment(simulation_type='real_time')


    @classmethod
    def load_dataset(cls, input_file):
        """ Creates simulation objects according to data from a JSON input file

        Parameters
        ==========
        file : string
            Path location of the JSON input file

        initial_edge_node_connection : boolean, optional
            Informs if the input file provides information on which clients are initially connected to edge nodes

        initial_placement : boolean, optional
            Informs if the input file provides information on the services initial placement
        """

        with open(f'data/{input_file}.json', 'r') as read_file:
            data = json.load(read_file)
            read_file.close()

        # Informing the simulation environment what's the dataset that will be used during the simulation
        Simulator.environment.dataset = input_file

        ##########################
        # SIMULATION COMPONENTS ##
        ##########################
        # Servers
        for server_data in data['servers']:
            # Creating object
            server = Server(id=None, cpu=None, memory=None, disk=None, updated=None)

            # Defining object attributes
            server.id = server_data['id']
            server.cpu_capacity = server_data['cpu_capacity']
            server.memory_capacity = server_data['memory_capacity']
            server.disk_capacity = server_data['disk_capacity']
            server.updated = server_data['updated']
            server.patch_duration = server_data['patch_duration']
            server.sanity_check_duration = server_data['sanity_check_duration']


        # Virtual Machines
        for vm_data in data['virtual_machines']:
            # Creating object
            vm = VirtualMachine(id=None, cpu=None, memory=None, disk=None)

            # Defining object attributes
            vm.id = vm_data['id']
            vm.cpu_demand = vm_data['cpu_demand']
            vm.memory_demand = vm_data['memory_demand']
            vm.disk_demand = vm_data['disk_demand']

            # Initial Placement
            server = Server.find_by_id(vm_data['server'])

            server.cpu_demand += vm.cpu_demand
            server.memory_demand += vm.memory_demand
            server.disk_demand += vm.disk_demand

            vm.server = server
            server.virtual_machines.append(vm)



        ######################
        ## Network Topology ##
        ######################
        topology = FatTree()

        # Creating links and nodes
        for link in data['network_topology']:
            
            # Creating nodes
            if link['nodes'][0]['type'] == 'Server':
                node_1 = Server.find_by_id(link['nodes'][0]['id'])
            else:
                node_1 = link['nodes'][0]['id']

            # Creating node 1 if it doesn't exists yet
            if node_1 not in topology:
                topology.add_node(node_1)
                for key, value in link['nodes'][0]['data'].items():
                    topology.nodes[node_1][key] = value

            if link['nodes'][1]['type'] == 'Server':
                node_2 = Server.find_by_id(link['nodes'][1]['id'])
            else:
                node_2 = link['nodes'][1]['id']

            # Creating node 2 if it doesn't exists yet
            if node_2 not in topology:
                topology.add_node(node_2)
                for key, value in link['nodes'][1]['data'].items():
                    topology.nodes[node_2][key] = value


            # Creating link if it wasn't created yet
            if not topology.has_edge(node_1, node_2):
                topology.add_edge(node_1, node_2)

                # Adding attributes to the link
                topology[node_1][node_2]['bandwidth'] = link['bandwidth']


        # Assigning 'topology' and 'simulation_environment' attributes to created objects
        objects = Server.all() + VirtualMachine.all()
        for obj in objects:
            obj.topology = topology
            obj.simulation_environment = Simulator.environment


    @classmethod
    def start(cls, **kwargs):
        """ Starts the simulation.
        """

        # Informing the simulation environment what's the maintenance strategy will be executed
        Simulator.environment.maintenance_strategy = kwargs['maintenance_strategy']

        # Starting the simulation
        Simulator.environment.start(tasks = lambda: Simulator.simulation_routine(**kwargs))


    @classmethod
    def simulation_routine(cls, **kwargs):
        """ Set of user-defined routines that execute at each simulation time step.
        """

        #############################
        ## Data Center Maintenance ##
        #############################
        if 'maintenance_strategy' in kwargs:
            yield Simulator.environment.env.process(Simulator.perform_datacenter_maintenance(kwargs['maintenance_strategy']))


    @classmethod
    def perform_datacenter_maintenance(cls, maintenance_strategy):
        """ Triggers data center maintenance strategies at each simulation step.

        Parameters
        ==========
        maintenance_strategy : string
            Name of a valid data center maintenance strategy
        """

        if maintenance_strategy == 'best_fit_like':
            yield Simulator.environment.env.process(best_fit_like())
        elif maintenance_strategy == 'first_fit_like':
            yield Simulator.environment.env.process(first_fit_like())
        elif maintenance_strategy == 'worst_fit_like':
            yield Simulator.environment.env.process(worst_fit_like())
        elif maintenance_strategy == 'greedy_least_batch':
            yield Simulator.environment.env.process(greedy_least_batch())
        elif maintenance_strategy == 'consolidation_aware':
            yield Simulator.environment.env.process(consolidation_aware())
        elif maintenance_strategy == 'hermes':
            yield Simulator.environment.env.process(hermes())
        elif maintenance_strategy == 'salus':
            yield Simulator.environment.env.process(salus())
        else:
            raise Exception('Invalid data center maintenance strategy! Exiting.')


    @classmethod
    def show_results(cls, output_file):
        """ Shows simulation results.
        """

        ################################
        ## Parsing simulation metrics ##
        ################################

        metrics_by_step = []
        overall_metrics = []

        dataset = Simulator.environment.dataset
        heuristic = Simulator.environment.maintenance_strategy


        #############################################################
        ## ITERATING OVER THE METRICS OF EACH SIMULATION TIME STEP ##
        #############################################################
        for metrics in Simulator.environment.metrics:
            # Server-related metrics
            consolidation_rate = 0
            occupation_rate = 0
            safeguarded_servers = 0
            vulnerable_servers = 0
            updated_servers = 0

            for server in metrics['servers']:
                # Security-related metrics
                if server['updated']:
                    safeguarded_servers += 1
                else:
                    vulnerable_servers += 1

                if server['update_step'] == metrics['maintenance_step']:
                    updated_servers += 1


                # Capacity-related metrics
                occupation_rate += server['occupation_rate']
                if len(server['virtual_machines']) == 0:
                    consolidation_rate += 1


            # Virtual-Machine-related metrics
            safeguarded_vms = 0
            vulnerable_vms = 0
            migrations = 0
            migrations_duration = []
            overall_migration_duration = 0
            average_migration_duration = 0
            longest_migration_duration = 0

            for vm in metrics['virtual_machines']:
                # Security-related metrics
                if vm['server_update_status']:
                    safeguarded_vms += 1
                else:
                    vulnerable_vms += 1

                # Migration-related metrics
                for migration in vm['migrations']:
                    if migration['maintenance_step'] == metrics['maintenance_step']:
                        migrations_duration.append(migration['duration'])


            # Post-processing security metrics
            vulnerability_surface = metrics['simulation_step'] * vulnerable_servers

            # Post-processing collected EdgeNode metrics
            occupation_rate /= len(metrics['servers'])
            consolidation_rate = consolidation_rate * 100 / len(metrics['servers'])


            # Post-processing collected Service metrics
            migrations = len(migrations_duration)
            if len(migrations_duration) > 0:
                overall_migration_duration = sum(migrations_duration)
                average_migration_duration = sum(migrations_duration) / len(migrations_duration)
                longest_migration_duration = max(migrations_duration)

            else:
                average_migration_duration = 0
                longest_migration_duration = 0


            # Printing Results
            print(f'\n=== MAINTENANCE STEP {metrics["maintenance_step"]}. SIMULATION STEP {metrics["simulation_step"]} ===')

            print(f'Maintenance Duration: {metrics["simulation_step"]}')
            print(f'Occupation Rate: {occupation_rate}')
            print(f'Safeguarded Servers: {safeguarded_servers}')
            print(f'Vulnerable Servers: {vulnerable_servers}')
            print(f'Updated Servers: {updated_servers}')
            print(f'Vulnerability Surface: {vulnerability_surface}')

            print(f'Safeguarded Virtual Machines: {safeguarded_vms}')
            print(f'Vulnerable Virtual Machines: {vulnerable_vms}')
            print(f'Migrations: {migrations}')
            print(f'    Overall Migration Duration: {overall_migration_duration}')
            print(f'    Average Migration Duration: {average_migration_duration}')
            print(f'    Longest Migration Duration: {longest_migration_duration}')


            # Consolidating step metrics
            metric_names = ['Dataset', 'Heuristic', 'Maintenance Step', 'Maintenance Duration',
            'Consolidation Rate', 'Occupation Rate', 'Safeguarded Servers', 'Vulnerable Servers',
            'Updated Servers', 'Safeguarded Virtual Machines', 'Vulnerable Virtual Machines',
            'Vulnerability Surface', 'Migrations', 'Overall Migration Duration',
            'Average Migration Duration', 'Longest Migration Duration']

            metric_values = [dataset, heuristic, metrics['maintenance_step'],
                metrics['simulation_step'], consolidation_rate, occupation_rate,
                safeguarded_servers, vulnerable_servers, updated_servers, safeguarded_vms,
                vulnerable_vms, vulnerability_surface, migrations, overall_migration_duration,
                average_migration_duration, longest_migration_duration]

            # Storing step metrics
            step_metrics = dict(zip(metric_names, metric_values))

            metrics_by_step.append(step_metrics)


        ###############################
        ## COMPUTING OVERALL METRICS ##
        ###############################
        metrics_by_step = pd.DataFrame(metrics_by_step)


        # Data center's resource usage
        consolidation_rate = metrics_by_step['Consolidation Rate'].mean()
        occupation_rate = metrics_by_step['Occupation Rate'].mean()

        # Data center's security
        vulnerability_surface = metrics_by_step['Vulnerability Surface'].sum()

        # Virtual machine migrations
        migrations = metrics_by_step['Migrations'].sum()
        overall_migration_duration = metrics_by_step['Overall Migration Duration'].sum()
        average_migration_duration = metrics_by_step['Average Migration Duration'].mean()
        longest_migration_duration = metrics_by_step['Longest Migration Duration'].max()



        print('\n\n=======================\n=== OVERALL RESULTS ===\n=======================')
        print(f'Dataset: {dataset}')
        print(f'Strategy: {heuristic}\n')
        print(f'Maintenance Duration: {metrics_by_step["Maintenance Duration"].iloc[-1]}')
        print(f'Consolidation Rate: {consolidation_rate}')
        print(f'Occupation Rate: {occupation_rate}')
        print(f'Vulnerability Surface: {vulnerability_surface}')

        print(f'Migrations: {migrations}')
        print(f'    Overall Migration Duration: {overall_migration_duration}')
        print(f'    Average Migration Duration: {average_migration_duration}')
        print(f'    Longest Migration Duration: {longest_migration_duration}')


        # Consolidating overall metrics
        metric_names = ['Dataset', 'Heuristic', 'Maintenance Duration', 'Consolidation Rate',
            'Occupation Rate', 'Vulnerability Surface', 'Migrations', 'Overall Migration Duration',
            'Average Migration Duration', 'Longest Migration Duration']

        metric_values = [dataset, heuristic, metrics_by_step['Maintenance Duration'].iloc[-1],
            consolidation_rate, occupation_rate, vulnerability_surface, migrations,
            overall_migration_duration, average_migration_duration, longest_migration_duration]

        
        # Storing overall metrics
        overall_metrics = [dict(zip(metric_names, metric_values))]
        overall_metrics = pd.DataFrame(overall_metrics)


        # Creating spreadsheet with the results
        writer = pd.ExcelWriter(f'{output_file}.xlsx')
        overall_metrics.to_excel(writer, 'Overall Results')
        metrics_by_step.to_excel(writer, 'Metrics By Maintenance Step')
        writer.save()


        if CSV_READY_OUTPUT:
            # Printing CSV-ready results
            print('\n\n=========================\n=== CSV-READY RESULTS ===\n=========================')
            print('\n== Overall Results ==')
            headers = [header for header in overall_metrics.head()]
            for column in headers:
                print(column, end='\t')
            print('\n')

            for index, row in overall_metrics.iterrows():
                for column in headers:
                    if type(row[column]) == float:
                        row[column] = round(row[column], 4)

                    print(f'{row[column]}', end='\t')
                print()

            print('\n== Metrics By Step ==')
            headers = [header for header in metrics_by_step.head()]
            for column in headers:
                print(column, end='\t')
            print('\n')

            for index, row in metrics_by_step.iterrows():
                for column in headers:
                    if type(row[column]) == float:
                        row[column] = round(row[column], 4)

                    print(f'{row[column]}', end='\t')
                print()

            print('\n== Safeguarded Servers By Step ==')
            safeguarded_servers_by_step = []
            maintenance_time_by_step = []
            for index, row in metrics_by_step.iterrows():
                maintenance_time_by_step.append(row['Maintenance Duration'])
                safeguarded_servers_by_step.append(row['Safeguarded Servers'])

            print(f'{heuristic} = {{ "name": "{heuristic}", "steps": {maintenance_time_by_step}, "safeguarded_servers": {safeguarded_servers_by_step} }}')
