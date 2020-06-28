from simulator.misc.object_collection import ObjectCollection
import simulator.misc.constants as constants

class VirtualMachine(ObjectCollection):
    instances = []

    def __init__(self, cpu, memory, disk):
        """ Initializes the virtual machine (VM).

        Parameters
        ==========
        cpu : int
            CPU demand of the VM

        memory : int
            Memory demand of the VM

        disk : int
            Disk demand of the VM
        """

        # Auto incremented ID
        self.id = VirtualMachine.count() + 1
        
        # Demand
        self.cpu_demand = cpu
        self.memory_demand = memory
        self.disk_demand = disk

        # Variable that denotes which server hosts the VM
        self.server = None

        # Adding the new object to the list of instances of its class
        VirtualMachine.instances.append(self)

    def migration_time(self):
        """ Migration equation presented by Severo et al. 2020. It calculates the
        migration duration. We multiply memory and disk demands by 1024 to convert
        these values from gigabytes to megabytes.

        Returns
        =======
        migration_time : int
            Amount of time needed to migrate a VM through the network to another host
        """

        migration_time = int(constants.SAVE_TIME + ((self.memory_demand * 1024 +
            self.disk_demand * 1024) / constants.NETWORK_BW) + constants.RESTORE_TIME)

        return(migration_time)

    def migrate(self, env, destination_server):
        """ Migrates a VM to a destination host.
        
        Parameters
        ==========
        env : SimPy.Environment
            Used to quantity the amount of simulation time spent by the migration

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

        yield env.timeout(migration_time)
        return(migration_time)

    def __str__(self):
        return(f'VM_{self.id}')
