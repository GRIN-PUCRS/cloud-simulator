from simulator.misc.object_collection import ObjectCollection

class Pod(ObjectCollection):
    instances = []

    def __init__(self):
        self.id = len(Pod.instances) + 1
        
        self.racks = []
        self.switches_aggregation = []

        Pod.instances.append(self)

    def __str__(self):
        return(f'Pod_{self.id}')

    def __repr__(self):
        return(f'Pod_{self.id}')
