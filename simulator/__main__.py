# USAGE EXAMPLE: python3 -B -m simulator -s="normal" -d="dataset75occupation" -m="salus" -o="salus"
# Python libraries
import random
import argparse

# General-purpose Simulator Modules
from simulator.simulator import Simulator
from simulator.misc.constants import SEED_VALUE


def main(simulation_type, dataset, maintenance_strategy, output_file):
    # Defining a seed value to enable reproducibility
    random.seed(SEED_VALUE)

    Simulator.create_environment(simulation_type=simulation_type)
    Simulator.load_dataset(input_file=dataset)
    Simulator.start(maintenance_strategy=maintenance_strategy)
    Simulator.show_results(output_file=output_file)


if __name__ == '__main__':
    # Parsing named arguments from the command line
    parser = argparse.ArgumentParser()

    parser.add_argument('--simulation-type', '-s', help='Type of simulation (e.g., as fast as possible OR wallclock speed)')
    parser.add_argument('--dataset', '-d', help='Input file containing the dataset for the simulation')
    parser.add_argument('--maintenance-strategy', '-m', help='Name of a valid data center maintenance strategy')
    parser.add_argument('--output-file', '-o', help='Name of output file to store simulation metrics')
    args = parser.parse_args()

    # Calling the main method
    main(simulation_type=args.simulation_type, dataset=args.dataset,
        maintenance_strategy=args.maintenance_strategy, output_file=args.output_file)
