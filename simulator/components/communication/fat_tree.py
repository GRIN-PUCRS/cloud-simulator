from fnss import get_capacities
from fnss.topologies import DatacenterTopology

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from matplotlib import pyplot as plt

from simulator.misc.object_collection import ObjectCollection
from simulator.components.infrastructure.switch import Switch
from simulator.components.infrastructure.rack import Rack
from simulator.components.infrastructure.server import Server

class FatTree(DatacenterTopology, ObjectCollection):
    """
    This class allows the creation of networks using the fat-tree topology

    Arguments:
        pods(List): List of Pod objects that will constitute the topology
        switches_core(List): List of core switches that will interconnect the pods
    """

    instances = []

    def __init__(self, pods, switches_core):
        # Calling DatacenterTopology constructor so that the FatTree object inherits all FNSS attributes
        super().__init__(self)

        # Defining instance attributes
        self.id = len(FatTree.instances) + 1
        self.type='fat_tree'
        self.k = len(pods)
        self.n_core = len(switches_core)
        self.name = f'Fat-Tree Topology (id={self.id}, k={self.k})'

        self.pods = pods
        self.switches_core = switches_core
        self.switches_aggregation = []
        self.switches_tor = []
        self.servers = []

        # Defining core switches as nodes
        for switch_core in self.switches_core:
            self.add_node(switch_core, layer='core', type='switch')

        # Defining servers and switches as nodes and creating links (edges) between them
        for pod in self.pods:
            print(pod)

            for switch_aggregation in pod.switches_aggregation:
                self.add_node(switch_aggregation, layer='aggregation', type='switch', pod=pod)
                self.switches_aggregation.append(switch_aggregation)

            for rack in pod.racks:
                print(f'  {rack}')
                self.add_node(rack.switch_tor, layer='edge', type='switch', pod=pod)
                self.switches_tor.append(rack.switch_tor)

                for server in rack.servers:
                    print(f'    {server}')
                    self.add_node(server, layer='leaf', type='host', pod=pod)
                    self.add_edge(rack.switch_tor, server, type='edge_leaf')
                    self.servers.append(server)

                for switch_aggregation in pod.switches_aggregation:
                    self.add_edge(switch_aggregation, rack.switch_tor, type='aggregation_edge')


        # Defining core switches as nodes and creating links between them and aggregation switches
        for switch_core in self.switches_core:
            for pod in self.pods:
                for switch_aggregation in pod.switches_aggregation:
                    self.add_edge(switch_core, switch_aggregation, type='core_aggregation')


        # Adding the created object to the list of FatTree instances
        FatTree.instances.append(self)

    def __str__(self):
        return(f'TOPO_{self.id}')

    def __repr__(self):
        return(f'TOPO_{self.id}')

    def visualize(self, output_file):
        # Coloring nodes according to their types
        color_map = []
        for node in self:
            if node in self.switches_core:
                color_map.append('#e63946')
            elif node in self.switches_aggregation:
                color_map.append('#e56b6f')
            elif node in self.switches_tor:
                color_map.append('#ffb5a7')
            elif node in self.servers:
                color_map.append('#dcdcdc')

        # Customizing links capacity representation
        edge_capacities = get_capacities(self)
        bw_unit = self.graph['capacity_unit']

        for edge in edge_capacities:
            edge_capacities[edge] = f'{edge_capacities[edge]}{bw_unit}'

        # Creating the plot
        plt.title(self.name)
        plt.margins(0.1)
        pos=graphviz_layout(self, prog='dot')
        nx.draw_networkx_edge_labels(self, pos, edge_labels=edge_capacities, font_size=7, label_pos=0.65)

        nx.draw(self, pos, labels={node:node for node in self.nodes()}, node_color=color_map, arrows=False, node_size=400, font_size=6, font_weight='bold')

        plt.savefig(output_file)
