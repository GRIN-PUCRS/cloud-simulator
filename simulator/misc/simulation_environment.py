# Python Libraries
import simpy

# General-purpose components
from simulator.components.misc.object_collection import ObjectCollection

# Simulator components
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine


class SimulationEnvironment(ObjectCollection):
    """ This class allows the creation objects that
    control the whole life cycle of simulations.
    """

    # Class attribute that allows the class to use ObjectCollection methods
    instances = []

    def __init__(self, simulation_type='normal'):
        """ Initializes the simulation object.
        """

        # Auto increment identifier
        self.id = SimulationEnvironment.count() + 1

        # Simulation type ('normal', 'real_time')
        self.type = simulation_type

        # List object that can be used to store any event that occurs during the simulation
        self.metrics = []

        # Number of maintenance steps
        self.maintenance_step = 1

        # SimPy's simulation environment
        self.env = None

        # SimPy's initial time
        self.initial_time = 0

        # SimPy's factor (how much real time passes with each step of simulation time on real-time simulations)
        self.factor = 1.0

        # SimPy's real-time simulations strictness (defines if SimPy will allow computations that take alonger than real time)
        self.strict = True

        # Dataset
        self.dataset = None

        # Data center maintenance strategy
        self.maintenance_strategy = None


        # Adding the new object to the list of instances of its class
        SimulationEnvironment.instances.append(self)


    def start(self, tasks):
        """ Starts the simulation.
        """

        # Creating SimPy environment
        if self.type == 'normal':
            self.env = simpy.Environment(initial_time=self.initial_time)
        elif self.type == 'real_time':
            self.env = simpy.rt.RealtimeEnvironment(initial_time=self.initial_time,
                factor=self.factor, strict=self.strict)


        # Executing the simulation
        self.env.process(self.run(tasks=tasks))

        self.env.run()


    def run(self, tasks):
        """ Triggers the set of events that ocurr during the simulation.
        """

        # The simulation goes on until all servers got the update
        while len(Server.nonupdated()) > 0:
            #########################################
            ## Running a set of user-defined tasks ##
            #########################################
            yield self.env.process(tasks())

            ####################################################################################
            ## Collecting simulation metrics for the current step and moving to the next step ##
            ####################################################################################
            self.collect_metrics()
            self.maintenance_step += 1


    def collect_metrics(self):
        """ Stores relevant events that occur during the simulation.
        """

        # Collecting Server metrics
        servers = []
        for server in Server.all():
            server_data = { 'server': server, 'occupation_rate': server.occupation_rate(),
                'cpu_capacity': server.cpu_capacity, 'memory_capacity': server.memory_capacity,
                'disk_capacity': server.disk_capacity, 'cpu_demand': server.cpu_demand,
                'memory_demand': server.memory_demand, 'disk_demand': server.disk_demand,
                'virtual_machines': server.virtual_machines, 'updated': server.updated,
                'update_step': server.update_step }

            servers.append(server_data)


        # Collecting VirtualMachine metrics
        virtual_machines = []
        for vm in VirtualMachine.all():
            vm_data = { 'cpu_demand': vm.cpu_demand, 'memory_demand': vm.memory_demand,
            'disk_demand': vm.disk_demand, 'server_update_status': vm.server.updated,
            'migrations': vm.migrations }

            virtual_machines.append(vm_data)


        # Creating the structure to accommodate simulation metrics
        self.metrics.append({'maintenance_step': self.maintenance_step, 'simulation_step': self.env.now,
            'servers': servers, 'virtual_machines': virtual_machines})
