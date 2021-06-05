# Python packages
import sys
import json
import random


# External libraries
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import fnss


# Workaround that allows this script to use classes from the simulator package
sys.path.append('..')


# Edge Simulator components
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine


####################
## HELPER METHODS ##
####################

###############################
## Probability distributions ##
###############################
def compute_distribution(n_items, distribution, valid_values=None):
    """ Computes the probability distribution for 'n_items' values. If user informs a predefined distribution
    for attribute values, the output gives a shuffled list of values to avoid intended unbalanced objects.

    Parameters
    ==========
    n_items : int
        Number of values for the picked numerical distribution

    distribution : List
        List containing 'n_items' values representing a numerical distribution
    Returns
    =======
    distribution_values : List
        Python list with size 'n_items' containing probability values defined according to a given numerical distribution
    """

    if valid_values == None:
        raise Exception('ERROR: you must inform a list of valid values for the attribute in the "valid_values" parameter')


    # Manually informed distribution
    if type(distribution) == list:            
        distribution_values = []
        for i, value in enumerate(valid_values):
            for _ in range(0, int(distribution[i])):
                distribution_values.append(value)

        # Computing leftover randomly to avoid disturbing the distribution
        leftover = n_items % len(valid_values)
        for i in range(leftover):
            random_valid_value = random.choice(valid_values)
            distribution_values.append(random_valid_value)

        random.shuffle(distribution_values)


    return(distribution_values)



#############
## Network ##
#############
def map_graph_nodes_to_objects(graph, new_node_objects):
    """ This method maps NetworkX graph nodes (integers by default) to Python objects. Please
    notice that this method performs the mapping according to the ordering of 'new_node_objects'.

    Parameters
    ==========
    graph : NetworkX graph
        NetworkX graph object

    new_node_objects : List
        List of objects that will replace default NetworkX nodes

    Returns
    =======
    graph : NetworkX graph
        NetworkX graph with Python objects as nodes
    """

    # Creating a dictionary where NetworkX nodes represent keys and Python objects represent values
    mapping = dict(zip(graph.nodes(), new_node_objects))

    # Replacing NetworkX original nodes by Python objects
    graph = nx.relabel_nodes(graph, mapping)

    return(graph)


def draw_network_topology():
    """ Creates an image of the network topology.
    """

    labels = {}
    for node in TOPOLOGY.nodes():
        # labels[node] = f'SV_{node.id}'
        labels[node] = node


    pos = graphviz_layout(TOPOLOGY, prog='dot')

    fig = plt.figure()
    plt.margins(0.06)

    nx.draw(TOPOLOGY, pos=pos, labels=labels, node_size=550, font_size=5, font_weight='bold')

    fig.savefig('topology.png', dpi=300)
    plt.show()



#############################
## OBJECT CREATION METHODS ##
#############################
def describe_simulation_scenario():
    """ Describes the simulation scenario with all created objects and its relationships
    """

    occupation_rate = 0
    for server in Server.all():
        occupation_rate += server.occupation_rate()
    occupation_rate = occupation_rate / Server.count()

    print(f'DATASET NAME: {OUTPUT_FILE_NAME}.json')
    print(f'DATA CENTER OCCUPATION: {round(occupation_rate)}% ({occupation_rate})')


def create_servers():
    """ Creates Server objects according to user-specified parameters.
    """

    for _ in range(SERVERS):
        # Creating object
        server = Server(id=None, cpu=None, memory=None, disk=None, updated=None)

        # Defining values for the object attributes
        server.id = Server.count()

        server.cpu_capacity = SERVERS_CAPACITY[0][0]
        server.memory_capacity = SERVERS_CAPACITY[0][1]
        server.disk_capacity = SERVERS_CAPACITY[0][2]
        server.updated = SERVERS_UPDATE_STATUS[0]
        server.patch_duration = SERVERS_PATCH_DURATION[0][0]
        server.sanity_check_duration = SERVERS_PATCH_DURATION[0][1]

        # Updating attribute lists after the object is created
        SERVERS_CAPACITY.pop(0)
        SERVERS_UPDATE_STATUS.pop(0)
        SERVERS_PATCH_DURATION.pop(0)


def create_virtual_machines():
    """ Creates VirtualMachine objects according to user-specified parameters.
    """

    for _ in range(VIRTUAL_MACHINES):
        # Creating object
        vm = VirtualMachine(id=None, cpu=None, memory=None, disk=None)

        # Defining values for the object attributes
        vm.id = VirtualMachine.count()

        vm.cpu_demand = VIRTUAL_MACHINES_DEMAND[0][0]
        vm.memory_demand = VIRTUAL_MACHINES_DEMAND[0][1]
        vm.disk_demand = VIRTUAL_MACHINES_DEMAND[0][2]

        # Updating attribute lists after the object is created
        VIRTUAL_MACHINES_DEMAND.pop(0)



##########################
## INITIAL VM PLACEMENT ##
##########################
def random_fit():
    """ Migrates VMs to random Server objects with resources to host them.
    """

    for vm in VirtualMachine.all():
        random_server = random.choice(Server.all())

        while not random_server.has_capacity_to_host(vm):
            random_server = random.choice(Server.all())


        # Assigning the random server to host the VM
        random_server.virtual_machines.append(vm)

        # Computing VM demand to its host server
        random_server.cpu_demand += vm.cpu_demand
        random_server.memory_demand += vm.memory_demand
        random_server.disk_demand += vm.disk_demand

        # Assigning the server as the VM host
        vm.server = random_server



########################
## DATASET PARAMETERS ##
########################

# Most kind of objects contain attributes with several valid values. To define these parameters,
# we must inform a list valid attributes and the number of occurrences of each of these attributes.

# Seed value that allows reproducibility while creating datasets
SEED = 1
random.seed(SEED)

# Defining output file name
OUTPUT_FILE_NAME = 'dataset75occupation'

# Servers (please take a look in the number of hosts of the topology before assigning a number of Server objects)
SERVERS = 128 # Number of Server objects

SERVERS_CAPACITY_VALUES = [[4, 4, 32], [8, 8, 64], [16, 16, 128]] # List of valid capacity values for Server objects (CPU, Memory, Disk)
SERVERS_CAPACITY_DISTRIBUTION = [int(SERVERS/len(SERVERS_CAPACITY_VALUES))
    for _ in range(len(SERVERS_CAPACITY_VALUES))]
SERVERS_CAPACITY = compute_distribution(n_items=SERVERS,
    distribution=SERVERS_CAPACITY_DISTRIBUTION, valid_values=SERVERS_CAPACITY_VALUES)

SERVERS_UPDATE_STATUS_VALUES = [False] # List of valid update status values for Server objects
SERVERS_UPDATE_STATUS_DISTRIBUTION = [SERVERS]
SERVERS_UPDATE_STATUS = compute_distribution(n_items=SERVERS,
    distribution=SERVERS_UPDATE_STATUS_DISTRIBUTION, valid_values=SERVERS_UPDATE_STATUS_VALUES)

SERVERS_PATCH_DURATION_VALUES = [[300, 600], [900, 1800], [2700, 5400]] # List of valid patch duration and sanity check values for Server objects
SERVERS_PATCH_DURATION_DISTRIBUTION = [int(SERVERS/len(SERVERS_PATCH_DURATION_VALUES))
    for _ in range(len(SERVERS_PATCH_DURATION_VALUES))]
SERVERS_PATCH_DURATION = compute_distribution(n_items=SERVERS,
    distribution=SERVERS_PATCH_DURATION_DISTRIBUTION, valid_values=SERVERS_PATCH_DURATION_VALUES)


# Virtual Machines
VIRTUAL_MACHINES = 370 # Number of VirtualMachine objects (99 VMs = 25% - 235 VMs = 50% - 370 VMs = 75%)

VIRTUAL_MACHINES_DEMAND_VALUES = [[1, 1, 8], [2, 2, 16], [4, 4, 32]] # List of valid demand values for VirtualMachine objects (CPU, Memory, Disk)
VIRTUAL_MACHINES_DEMAND_DISTRIBUTION = [int(VIRTUAL_MACHINES/len(VIRTUAL_MACHINES_DEMAND_VALUES))
    for _ in range(len(VIRTUAL_MACHINES_DEMAND_VALUES))]
VIRTUAL_MACHINES_DEMAND = compute_distribution(n_items=VIRTUAL_MACHINES,
    distribution=VIRTUAL_MACHINES_DEMAND_DISTRIBUTION, valid_values=VIRTUAL_MACHINES_DEMAND_VALUES)



#######################
## Creating topology ##
#######################

# Creating NetworkX graph with 'NETWORK_NODES' nodes
NETWORK_NODES = SERVERS
# Topology model options: 'Fat-Tree'
TOPOLOGY_NAME = 'Fat-Tree'

if TOPOLOGY_NAME == 'Fat-Tree':
    # https://fnss.readthedocs.io/en/latest/apidoc/generated/fnss.topologies.datacenter.fat_tree_topology.html
    TOPOLOGY = fnss.topologies.datacenter.fat_tree_topology(k=8)



######################
## CREATING OBJECTS ##
######################
create_servers()
create_virtual_machines()



###################################################################################
## MAPPING ORIGINAL GRAPH NODES THAT REPRESENT HOSTS TO PYTHON OBJECTS (SERVERS) ##
###################################################################################
servers = [sv for sv in Server.all()]
new_nodes = []
for node in TOPOLOGY.nodes(data=True):
    if node[1]['type'] == 'host':
        new_nodes.append(servers.pop(0))
    else:
        new_nodes.append(node[0])


TOPOLOGY = map_graph_nodes_to_objects(TOPOLOGY, new_nodes)


# Updating created object's topology property
for server in Server.all():
    server.topology = TOPOLOGY


for vm in VirtualMachine.all():
    vm.topology = TOPOLOGY


# Number of Service objects
LINKS = len(TOPOLOGY.edges())

LINK_BANDWIDTH_VALUES = [125] # List of valid bandwidth values for network links
LINK_BANDWIDTH_DISTRIBUTION = [LINKS]
LINK_BANDWIDTH = compute_distribution(n_items=LINKS, distribution=LINK_BANDWIDTH_DISTRIBUTION,
    valid_values=LINK_BANDWIDTH_VALUES)


# Defining link attributes
for link in TOPOLOGY.edges(data=True):
    TOPOLOGY[link[0]][link[1]]['bandwidth'] = LINK_BANDWIDTH[0]

    # Updating attribute lists after the link is updated
    LINK_BANDWIDTH.pop(0)



##########################
## INITIAL VM PLACEMENT ##
##########################
random_fit()



#####################################
## PRINTING THE GENERATED SCENARIO ##
#####################################

describe_simulation_scenario() # Describing the created scenario

# draw_network_topology() # Generating an image of the NetworkX topology



##########################
## CREATING OUTPUT FILE ##
##########################
# Creating dataset dictionary that will be converted to a JSON object
dataset = {}


# Servers
servers = [{ 'id': sv.id, 'cpu_capacity': sv.cpu_capacity, 'memory_capacity': sv.memory_capacity,
    'disk_capacity': sv.disk_capacity, 'virtual_machines': [vm.id for vm in sv.virtual_machines],
    'updated': sv.updated, 'patch_duration': sv.patch_duration, 'sanity_check_duration': sv.sanity_check_duration }
    for sv in Server.all()]


# Virtual Machines
virtual_machines = [{ 'id': vm.id, 'cpu_demand': vm.cpu_demand, 'memory_demand': vm.memory_demand,
    'disk_demand': vm.disk_demand, 'server': vm.server.id } for vm in VirtualMachine.all()]


# Network topology
network_links = []
for link in TOPOLOGY.edges(data=True):
    # Gathering attributes from link nodes
    node_1 = {}
    if type(link[0]) == Server:
        node_1['type'] = 'Server'
        node_1['id'] = link[0].id
    else:
        node_1['type'] = 'int'
        node_1['id'] = link[0]
    node_1['data'] = TOPOLOGY.node[link[0]]

    node_2 = {}
    if type(link[1]) == Server:
        node_2['type'] = 'Server'
        node_2['id'] = link[1].id
    else:
        node_2['type'] = 'int'
        node_2['id'] = link[1]
    node_2['data'] = TOPOLOGY.node[link[1]]

    # Consolidating link data into a dictionary
    nodes = [node_1, node_2]
    bandwidth = TOPOLOGY[link[0]][link[1]]['bandwidth']
    network_links.append({ 'nodes': nodes, 'bandwidth': bandwidth })


# Consolidating all created dictionaries into the 'dataset' dictionary
dataset['servers'] = servers
dataset['virtual_machines'] = virtual_machines
dataset['network_topology'] = network_links


# Creating output file
with open(f'{OUTPUT_FILE_NAME}.json', 'w') as output_file:
    json.dump(dataset, output_file, indent=4)
