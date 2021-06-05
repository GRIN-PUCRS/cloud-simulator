# General-purpose simulator modules
from simulator.components.misc.object_collection import ObjectCollection
import simulator.misc.constants as constants


class VirtualMachine(ObjectCollection):
    """ This class allows the creation of virtual machine (VM) objects.
    """

    instances = []

    def __init__(self, id, cpu, memory, disk):
        """ This method creates a VM object.

        Parameters
        ==========
        id : int
            Unique identifier

        cpu : int
            CPU demand of the VM

        memory : int
            Memory demand of the VM

        disk : int
            Disk demand of the VM
        """

        # Unique identifier
        self.id = id
        
        # VM demand
        self.cpu_demand = cpu
        self.memory_demand = memory
        self.disk_demand = disk

        # Server that hosts the VM
        self.server = None

        # Helper list that allows us to keep track of all VM migrations
        self.migrations = []

        # Network topology
        self.topology = None

        # Simulation environment
        self.simulation_environment = None


        # Adding the new object to the list of instances of its class
        VirtualMachine.instances.append(self)


    def __str__(self):
        return(f'VM_{self.id}')


    def __repr__(self):
        return(f'VM_{self.id}')


    def demand(self):
        """ Computes the overall VM demand. We use the geometric mean as we compute
        demand attributes differently. More specifically, we represent 'cpu_demand' as
        means of number of CPU cores, while we represent 'memory_demand' and 'disk_demand'
        as gigabytes.

        Returns
        =======
        demand : Float
            Overall VM's demand
        """

        # Computing VM's overall demand
        demand = (self.cpu_demand * self.memory_demand * self.disk_demand) ** (1/3)

        return(demand)


    def migration_time(self):
        """ Migration equation presented by Severo et al. that computes the
        migration duration. We multiply memory and disk demands by 1024 to convert
        these values from gigabytes to megabytes.

        Returns
        =======
        migration_time : int
            Amount of time needed to migrate a VM through the network to another host
        """
        network_delay = (self.memory_demand * 1024 + self.disk_demand * 1024) / constants.NETWORK_BW
        migration_time = int(constants.SAVE_TIME + network_delay + constants.RESTORE_TIME)

        return(migration_time)


    def migrate(self, destination_server):
        """ Migrates the VM to a destination host.
        
        Parameters
        ==========
        destination_serer : Server
            Server object to which the VM will be migrated
        """

        # Removes the VM from the origin server and updates its demand
        origin_server = self.server
        origin_server.virtual_machines.remove(self)

        origin_server.cpu_demand -= self.cpu_demand
        origin_server.memory_demand -= self.memory_demand
        origin_server.disk_demand -= self.disk_demand

        # Adds the VM to the destination server and updates its demand
        destination_server.virtual_machines.append(self)

        destination_server.cpu_demand += self.cpu_demand
        destination_server.memory_demand += self.memory_demand
        destination_server.disk_demand += self.disk_demand

        self.server = destination_server

        # Gathering the migration time for the VM
        migration_time = self.migration_time()

        # Storing migration metadata to allow post-simulation analysis
        self.migrations.append({'maintenance_step': self.simulation_environment.maintenance_step,
            'duration': migration_time, 'origin': origin_server,
            'destination': destination_server})

        return(migration_time)
