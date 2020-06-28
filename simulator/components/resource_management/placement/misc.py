from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine

def vms_ordering(ordering=None):
    """ Sorts the list of VMs based on a given order. Currently,
    we can specify "Increasing" and "Decreasing" as parameters.

    Parameters
    ==========
    ordering : String
        Ordering parameter that dictates how VMs are organized

    Returns
    =======
    vms : List
        List of VMs sorted according to the chosen method

    """
    if ordering == 'Increasing':
        # Sorting VMs by its demand (increasing)
        vms = sorted(VirtualMachine.all(), key=lambda vm:
            (vm.cpu_demand, vm.memory_demand, vm.disk_demand))

    elif ordering == 'Decreasing':
        # Sorting VMs by its demand (decreasing)
        vms = sorted(VirtualMachine.all(), key=lambda vm:
            (-vm.cpu_demand, -vm.memory_demand, -vm.disk_demand))

    else:
        # Gathering all created VMs with no explicit order
        vms = VirtualMachine.all()

    return(vms)

def show_metrics(dataset, heuristic, output_file=None):
    """ Presents information and metrics of the performed placement
    and optionally stores these results into an output CSV file.

    Currently, this method outputs the following metrics:
        - Servers occupation rate
        - Servers consolidation rate

    Parameters
    ==========
    dataset : String
        Name of the used dataset

    heuristic : STring
        Name of the used placement heuristic

    output_file : String
        Optional parameters regarding the name of the output CSV file
    """

    # Servers occupation rate
    occupation_rate = sum(sv.occupation_rate() for sv in Server.all()) / len(Server.used_servers())
    
    # Servers consolidation rate
    consolidation_rate = Server.consolidation_rate()

    # Prints out the placement metrics
    print('========================\n== SIMULATION RESULTS ==\n========================')

    print(f'Dataset: "{dataset}"')
    print(f'Placement Strategy: {heuristic}\n')

    print(f'Consolidation Rate: {consolidation_rate}')
    print(f'Occupation Rate: {occupation_rate}\n')

    print('Placement:')
    for server in Server.all():
        vms = [vm.id for vm in server.virtual_machines]
        print(f'SV_{server.id}. VMs: {vms}')

    # If the output_file parameter was provided, stores the placement results into a CSV file
    if output_file:

        with open(output_file, mode='w') as csv_file:
            output_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # Creating header
            output_writer.writerow(['Dataset', 'Strategy', 'No. of Servers', 'No. of VMs',
                'Occupation Rate', 'Consolidation Rate'])

            # Creating body
            output_writer.writerow([dataset, heuristic, Server.count(), VirtualMachine.count(),
                occupation_rate, consolidation_rate])
