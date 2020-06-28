from simulator.misc.object_collection import ObjectCollection

class Rack(ObjectCollection):
    instances = []

    def __init__(self):
        self.id = len(Rack.instances) + 1
        self.servers = []
        self.switch_tor = None

        Rack.instances.append(self)

    def __str__(self):
        return(f'RACK_{self.id}')

    def __repr__(self):
        return(f'Rack_{self.id}')

    def add_server(self, server):
        self.servers.append(server)
