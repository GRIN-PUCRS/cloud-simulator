from simulator.misc.object_collection import ObjectCollection
import simulator.misc.constants as constants

class Server(ObjectCollection):
    instances = []

    def __init__(self, cpu, memory, disk):
        """ Initializes the server.

        Parameters
        ==========
        cpu : int
            CPU capacity of the server

        memory : int
            Memory capacity of the server

        disk : int
            Disk capacity of the server
        """

        # Auto incremented ID
        self.id = Server.count() + 1
        
        # Capacity
        self.cpu_capacity = cpu
        self.memory_capacity = memory
        self.disk_capacity = disk
        
        # Demand
        self.cpu_demand = 0
        self.memory_demand = 0
        self.disk_demand = 0

        # Rack in which the server is located
        self.rack = None

        # List used to store the hosted virtual machines
        self.virtual_machines = []
        
        # Server update status
        self.updated = False

        # Adding the new object to the list of instances of its class
        Server.instances.append(self)

    def __str__(self):
        return(f'SV_{self.id}')

    def calculate_demand(self):
        """ Calculates the demand of a server based on the list of VMs it hosts.
        """

        self.cpu_demand = 0
        self.memory_demand = 0
        self.disk_demand = 0

        for vm in self.virtual_machines:
            self.cpu_demand += vm.cpu_demand
            self.memory_demand += vm.memory_demand
            self.disk_demand += vm.disk_demand

    def overall_demand(self):
        """ Calculates the overall server demand using the geometric mean.

        Returns
        =======
        demand : float
            Overall server demand
        """

        demand = (self.cpu_demand * self.memory_demand * self.disk_demand)**(1/3)

        return(demand)


    def has_capacity_to_host(self, vm):
        """ Checks if whether a server has resources or not to host a VM.

        Returns
        =======
        True OR False
            The response that tells us if a given server has resources to host a VM
        """

        return(self.cpu_demand + vm.cpu_demand <= self.cpu_capacity and
            self.memory_demand + vm.memory_demand <= self.memory_capacity and
            self.disk_demand + vm.disk_demand <= self.disk_capacity)

    def update_cost(self):
        """ Update cost equation defined by Severo et al. 2020. The longer it takes
        to migrate all the VMs of a server, the higher will be its update cost score.

        Returns
        =======
        update_cost : int
            Update cost of a server (based on the migration cost of its VMs)
        """

        update_cost = 0

        for vm in self.virtual_machines:
            # Gathering the migration time for the VM
            update_cost += vm.migration_time()

        return(update_cost)

    def occupation_rate(self):
        """ Calculates the occupation rate of a server.

        Returns
        =======
        occupation_rate : Float
            Occupation rate of a server
        """

        cpu_usage_percentage = self.cpu_demand * 100 / self.cpu_capacity
        memory_usage_percentage = self.memory_demand * 100 / self.memory_capacity
        disk_usage_percentage = self.disk_demand * 100 / self.disk_capacity

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
        """ Calculates the consolidation rate of the group of servers.

        Returns
        =======
        consolidation_rate : Float
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
            i) It must be non-updated
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
        def delta(x,y):
            return abs(x-y)
        # Verifying if all VMs could be hosted by the list of servers
        for vm in virtual_machines:
            
            # Sorting servers according to their current capacity (descending)
            servers = sorted(servers, key=lambda sv:
                (-delta(sv.cpu_demand, sv.cpu_capacity), -delta(sv.memory_demand, sv.memory_capacity), -delta(sv.disk_demand, sv.disk_capacity)))

            for server in servers:
                if server.has_capacity_to_host(vm):
                    server.cpu_demand += vm.cpu_demand
                    server.memory_demand += vm.memory_demand
                    server.disk_demand += vm.disk_demand

                    vms_allocated += 1
                    break
        
        # Recalculating server demand
        for server in servers:
            server.calculate_demand()

        return(len(virtual_machines) == vms_allocated)
