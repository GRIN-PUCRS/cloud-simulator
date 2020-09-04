import sys
import simpy

from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine
from simulator.misc.load_dataset import load_dataset
from simulator.components.resource_management.maintenance.strategies.vulnerability_surface import vulnerability_surface
from simulator.components.resource_management.maintenance.strategies.best_fit import best_fit
from simulator.components.resource_management.maintenance.strategies.worst_fit import worst_fit
from simulator.components.resource_management.maintenance.strategies.first_fit import first_fit
from simulator.components.resource_management.maintenance.strategies.consolidation_aware import consolidation_aware
from simulator.components.resource_management.maintenance.strategies.delay_aware import delay_aware
from simulator.components.resource_management.maintenance.misc import show_metrics

def main():
    # Loading the dataset from a JSON file. Currently available options:
    # 'data/input.json'
    # 'data/paper_example.json'
    # 'data/dataset_occupation-25.json'
    # 'data/dataset_occupation-50.json'
    # 'data/dataset_occupation-75.json'
    dataset = 'data/dataset_occupation-25.json'
    load_dataset(dataset, initial_placement=True)

    # Maintenance data to be gathered during the simulation
    maintenance_data = []

    # Defines SimPy simulation environment
    env = simpy.Environment(initial_time=0) # Tells SimPy to simulate as fast as possible

    # Specifies the maintenance strategy. Currently available options:
    # i) best_fit
    # ii) first_fit
    # iii) worst_fit
    # iv) consolidation_aware
    # v) delay_aware
    # vi) vulnerability_surface

    # env.process(delay_aware(env, maintenance_data))
    # env.process(consolidation_aware(env, maintenance_data))
    env.process(vulnerability_surface(env, maintenance_data))

    # Starts the simulation
    env.run()

    # Prints out the maintenance results and optionally stores metrics into an output CSV file
    show_metrics(dataset, maintenance_data, output_file=None, verbose=True)

if __name__ == '__main__':
    main()
