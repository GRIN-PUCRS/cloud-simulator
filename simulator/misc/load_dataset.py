import json

from simulator.misc.object_collection import ObjectCollection
from simulator.components.infrastructure.server import Server
from simulator.components.application.virtual_machine import VirtualMachine


def load_dataset(file, initial_placement=False):
    with open(file, "r") as read_file:
        data = json.load(read_file)

    # Creating Server objects
    for server in data['servers']:
        Server(server['cpu'], server['memory'], server['disk'])

    # Creating VirtualMachine objects
    for virtual_machine in data['virtual_machines']:
        VirtualMachine(virtual_machine['cpu'], virtual_machine['memory'], virtual_machine['disk'])

    # If the initial_placement flag is provided, applies the initial VM placement
    if initial_placement:
        for server_data in data['servers']:
            server = Server.find_by_id(server_data['id'])

            for vm_id in server_data['virtual_machines']:
                virtual_machine = VirtualMachine.find_by_id(vm_id)

                server.virtual_machines.append(virtual_machine)

                server.cpu_demand += virtual_machine.cpu_demand
                server.memory_demand += virtual_machine.memory_demand
                server.disk_demand += virtual_machine.disk_demand

                virtual_machine.server = server
