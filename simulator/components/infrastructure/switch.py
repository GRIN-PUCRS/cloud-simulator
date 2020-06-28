from simulator.misc.object_collection import ObjectCollection

class Switch(ObjectCollection):
    instances = []

    def __init__(self):
        self.id = len(Switch.instances) + 1

        Switch.instances.append(self)

    def __str__(self):
        return(f'SW_{self.id}')

    def __repr__(self):
        return(f'Switch_{self.id}')
