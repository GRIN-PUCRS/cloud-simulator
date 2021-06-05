# General-purpose simulator modules
from simulator.components.misc.object_collection import ObjectCollection
import simulator.misc.constants as constants


class Server(ObjectCollection):
    """ This class allows the creation of server objects.
    """

    instances = []

    def __init__(self, id, cpu, memory, disk, updated):
        """ This method creates a VM object.

        Parameters
        ==========
        id : int
            Unique identifier

        cpu : int
            CPU capacity of the server

        memory : int
            Memory capacity of the server

        disk : int
            Disk capacity of the server

        updated : boolean
            Initial update status
        """

        # Unique identifier
        self.id = id
        
        # Capacity
        self.cpu_capacity = cpu
        self.memory_capacity = memory
        self.disk_capacity = disk
        
        # Demand
        self.cpu_demand = 0
        self.memory_demand = 0
        self.disk_demand = 0

        # List hosted virtual machines
        self.virtual_machines = []
        
        # Server update status
        self.updated = updated
        self.update_step = None

        # Server patch specs
        self.patch_duration = 0
        self.sanity_check_duration = 0

        # Network topology
        self.topology = None

        # Simulation environment
        self.simulation_environment = None

        # Adding the new object to the list of instances of its class
        Server.instances.append(self)


    def __str__(self):
        return(f'Server_{self.id}')


    def __repr__(self):
        return(f'Server_{self.id}')


    def update(self):
        """ Updates the server.

        Returns
        =======
        maintenance_duration : int
            Server's maintenance duration
        """

        self.updated = True
        self.update_step = self.simulation_environment.maintenance_step

        return(self.maintenance_duration())


    def capacity(self):
        """ Computes the overall server capacity. We use the geometric mean as we compute
        capacity attributes differently. More specifically, we represent 'cpu_capacity' as
        means of number of CPU cores, while we represent 'memory_capacity' and 'disk_capacity'
        as gigabytes.

        Returns
        =======
        capacity : int
            Overall server's capacity
        """

        # Computing server's overall capacity
        overall_capacity = (self.cpu_capacity * self.memory_capacity * self.disk_capacity) ** (1/3)

        return(overall_capacity)


    def demand(self):
        """ Computes the overall server demand. We use the geometric mean as we compute
        demand attributes differently. More specifically, we represent 'cpu_demand' as
        means of number of CPU cores, while we represent 'memory_demand' and 'disk_demand'
        as gigabytes.

        Returns
        =======
        demand : int
            Overall server's demand
        """

        # Computing server's demand
        self.compute_demand()

        # Computing server's overall demand
        overall_demand = (self.cpu_demand * self.memory_demand * self.disk_demand) ** (1/3)

        return(overall_demand)


    def compute_demand(self):
        """ Computes the server's demand based on the list of VMs it hosts.
        """

        self.cpu_demand = 0
        self.memory_demand = 0
        self.disk_demand = 0

        for vm in self.virtual_machines:
            self.cpu_demand += vm.cpu_demand
            self.memory_demand += vm.memory_demand
            self.disk_demand += vm.disk_demand


    def has_capacity_to_host(self, vm):
        """ Checks if whether a server has resources or not to host a VM.

        Parameters
        ==========
        vm : VirtualMachine
            Virtual machine we want to know if the server has capacity to host

        Returns
        =======
        True OR False
            Answer that tells us if the server has resources to host the virtual machine
        """

        # Updating server's demand
        self.compute_demand()

        return(self.cpu_demand + vm.cpu_demand <= self.cpu_capacity and
            self.memory_demand + vm.memory_demand <= self.memory_capacity and
            self.disk_demand + vm.disk_demand <= self.disk_capacity)


    def drain_duration(self):
        """ Calculates the time needed to empty the server.

        Returns
        =======
        drain_duration : itn
            Time needed to empty the server
        """

        # Calculating the amount of time needed to empty the server
        drain_duration = 0
        for vm in self.virtual_machines:
            # Gathering the migration time for each VM hosted on the server
            drain_duration += vm.migration_time()

        return(drain_duration)


    def maintenance_duration(self):
        """ Patch duration scheme defined by Severo et al. In addition to the
        patching and sanity checking durations, it considers the amount of time
        it takes to empty the server.

        Returns
        =======
        patch_duration : int
            Time it takes to maintenance the server
        """

        # Calculating the server's maintenance duration
        maintenance_duration = self.drain_duration() + self.patch_duration + self.sanity_check_duration

        return(maintenance_duration)


    def occupation_rate(self):
        """ Computes the occupation rate of a server.

        Returns
        =======
        occupation_rate : Float
            Occupation rate of a server
        """

        # Updating server's demand
        self.compute_demand()

        # Gathering current resource usage (in percent)
        cpu_usage_percentage = self.cpu_demand * 100 / self.cpu_capacity
        memory_usage_percentage = self.memory_demand * 100 / self.memory_capacity
        disk_usage_percentage = self.disk_demand * 100 / self.disk_capacity

        # Computing server's occupation rate
        occupation_rate = (cpu_usage_percentage + memory_usage_percentage + disk_usage_percentage) / 3

        return(occupation_rate)


    @classmethod
    def used_servers(cls):
        """ Gets the list of used servers (i.e., servers that are hosting VMs).

        Returns
        =======
        used_servers : List
            List of servers hosting VMs
        """

        used_servers = [sv for sv in Server.all() if len(sv.virtual_machines) > 0]

        return(used_servers)


    @classmethod
    def consolidation_rate(cls):
        """ Computes the consolidation rate of the group of servers.

        Returns
        =======
        consolidation_rate : float
            Consolidation rate of the group of servers
        """

        used_servers = len(Server.used_servers())

        consolidation_rate = 100 - (used_servers * 100 / Server.count())

        return(consolidation_rate)


    @classmethod
    def nonupdated(cls):
        """ Gathers the list of servers that were not updated yet.
        
        Returns
        =======
        List
            List of nonupdated servers
        """

        return([sv for sv in Server.all() if sv.updated == False])


    @classmethod
    def updated(cls):
        """ Gathers the list of servers that already received the patch.
        
        Returns
        =======
        List
            List of updated servers
        """

        return([sv for sv in Server.all() if sv.updated == True])
    

    @classmethod
    def ready_to_patch(cls):
        """ Gathers the list of servers ready to be patched. This decision depends on
        specific maintenance demands. By default, to be considered ready for maintenance,
        a server must respect two conditions:
            i) It must be nonupdated
            ii) It must be empty (i.e., not hosting any VM)

        Returns
        =======
        servers_to_update : List
            List of servers ready to be patched
        """

        servers_to_update = [server for server in Server.nonupdated()
            if len(server.virtual_machines) == 0]

        return(servers_to_update)


    @classmethod
    def can_host_vms(cls, servers, virtual_machines):
        """ Checks whether a set of servers have resources or not to host a collection of VMs.
        We look for this as a Bin-Packing problem, so use a Best-Fit to avoid resource wastage.
        
        Parameters
        ==========
        servers : List
            List of candidate host servers for the VMs
        
        virtual machines : List
            List of VMs that we will try to host

        Returns
        =======
        True OR False
            The response that tells us whether the set of servers did manage or not
            to host all VMs within the list.
        """

        vms_allocated = 0

        virtual_machines = sorted(virtual_machines, key=lambda vm: -vm.demand())

        # Verifying if all VMs could be hosted by the list of servers
        for vm in virtual_machines:
            # Sorting servers according to their demand (descending)
            servers = sorted(servers, key=lambda sv: -sv.occupation_rate())

            for server in servers:
                if vm.server != server and server.has_capacity_to_host(vm):
                    server.cpu_demand += vm.cpu_demand
                    server.memory_demand += vm.memory_demand
                    server.disk_demand += vm.disk_demand

                    vms_allocated += 1
                    break
        
        # Recomputing servers demand
        for server in servers:
            server.compute_demand()

        return(len(virtual_machines) == vms_allocated)
