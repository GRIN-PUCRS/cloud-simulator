# General-purpose simulator modules
from fnss.topologies import DatacenterTopology
from simulator.components.misc.object_collection import ObjectCollection


class FatTree(DatacenterTopology, ObjectCollection):
    """ This class allows the creation of networks using the fat-tree topology.
    """

    instances = []

    def __init__(self):
        """ This method creates a FatTree object.
        """

        # Calling DatacenterTopology constructor so that the object inherits all FNSS features
        super().__init__(self)

        # Unique identifier
        self.id = len(FatTree.instances) + 1

        # Adding the new object to the list of instances of its class
        FatTree.instances.append(self)


    def __str__(self):
        return(f'TOPO_{self.id}')


    def __repr__(self):
        return(f'TOPO_{self.id}')
