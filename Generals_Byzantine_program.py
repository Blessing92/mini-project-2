import sys
import time
import threading
import _thread
import random

from node import Node
from state import State, Election
from utilities import make_the_connections


global message
message = []
sockets = []
used_ports = []
all_threads = []
resources = False


class MyTestNode (Node):
    def __init__(self, host, port, id):
        self.ownMessage = []
        self.logical_time = 5 + time.process_time()
        self.timestamp = 0
        self.time_to_hold_cs = 10
        self.state = State.NF
        self.majority = ""
        self.election_status = Election.secondary
        self.local_count = 0
        self.queues = []
        self.sent_to_all = False

        super(MyTestNode, self).__init__(host, port, id)
        global message
        message.append("mytestnode started")

    def outbound_node_connected(self, node):
        global message
        message.append("outbound_node_connected: " + node.id)

    def inbound_node_connected(self, node):
        global message
        message.append("inbound_node_connected: " + node.id)

    def inbound_node_disconnected(self, node):
        global message
        message.append("inbound_node_disconnected: " + node.id)

    def outbound_node_disconnected(self, node):
        global message
        message.append("outbound_node_disconnected: " + node.id)

    def node_message(self, node, data):
        global message
        num_node = len(sockets) - 1
        self.ownMessage.append(self.id + " node_message from " +
                               node.id + ": " + str(data) + " port: " + str(node.port))

          

    def node_disconnect_with_outbound_node(self, node):
        global message
        message.append(
            "node wants to disconnect with oher outbound node: " + node.id)

    def node_request_to_stop(self):
        global message
        message.append("node is requested to stop!")


# def tick(running, node):
#     while running:
#         if not node.sent_to_all:
#             time.sleep(node.logical_time)
#             node.state = State.WANTED
#             my_id = node.id
#             send_time = time.process_time()
#             new_msg = "resource" + "," + node.id + "," + str(send_time)

#             # Send messages to other nodes for accessing the critical section
#             for node in sockets:
#                 if node.id == my_id:
#                     node.send_to_nodes(new_msg)
#                     node.timestamp = send_time
#                     time.sleep(5)
#                     node.sent_to_all = True
#                     running = False

 
def start(args):

    port = 10001
    number_of_processes = int(args)

    for node_id in range(number_of_processes):
        node = MyTestNode(host="127.0.0.1", port=port, id="G" + str(node_id+1))
        used_ports.append(port)
        port += 1
        node.start()
        sockets.append(node)

    # Node 1 connect to other nodes
    make_the_connections(sockets)

    # Select for the Leader in the begining of the program
    for node in sorted(sockets, key=lambda node: node.id):
        if node.id == "G1":
            node.election_status = Election.primary

    running = True

    for node in sockets:
        # start a separate thread for every node to control their logical time
        # _thread.start_new_thread(tick, (running, node))
        pass

    while running:
        inp = input("Enter command (exit command to quit): ").lower()
        cmd = inp.split(" ")

        command = cmd[0]

        if command == 'actual-order':
            is_good = is_good_entry(cmd)
            if is_good:
                actual_order(cmd[1])
                for node in sorted(sockets, key=lambda node: node.id):
                    print(str(node.id) + ", " + str(node.election_status.name) + ", majority=" + str(node.majority) + ", state=" + str(node.state.name))
        
        # g-state ID “State”, where ID is the general ID and state is either “Faulty” or “Non-faulty”. For instance,
        elif command == 'g-state':
            if len(cmd) == 1:
                for node in sorted(sockets, key=lambda node: node.id):
                    print(str(node.id) + ", " + str(node.election_status.name) + ", state=" + str(node.state.name))
            elif len(cmd) == 3:
                if not cmd[1].isnumeric():
                    print(cmd[1], " is not a valid integer")
                else:
                    if str(cmd[2]).lower() != "faulty" and str(cmd[2]).lower() != "non-faulty":
                        print("Usage: g-state <ID> <'faulty' or 'non-faulty'>")
                    else:
                        change_state(cmd[1], cmd[2])
            else:
                print("Usage: g-state <ID> <'faulty' or 'non-faulty'>")
        
        # $ g-kill ID, this commands remove a general based on its ID. For instance
        elif command == "g-kill":
            if len(cmd) != 2:
                print("Usage: g-kill <ID>")
            else:
                if not cmd[1].isnumeric():
                    print(cmd[1], " is not a valid integer")
                else:
                    kill_general(cmd[1])


        elif command == 'exit':
            for node in sockets:
                node.stop()
            print(
                "Program Terminated Successfully! Please wait for all the nodes to stop...")
            sys.exit()
        else:
            print("Invalid command! Please try again...")


def actual_order(action):
    for node in sorted(sockets, key=lambda node: node.id):
        node.majority = str(action)

# g-state ID “State”, where ID is the general ID and state is either “Faulty” or “Non-faulty”. For instance,
def change_state(id_number, state):
    node_id = 'G'+id_number
    for node in sockets:
        if node.id == node_id:
            if state == 'faulty':
                node.state = State.F
            elif state == 'non-faulty':
                node.state = State.NF
    
    for node in sorted(sockets, key=lambda node: node.id):
        print(str(node.id) + ", state=" + str(node.state.name))


# $ g-kill ID, this commands remove a general based on its ID. For instance
def kill_general(general_id):
    node_id = 'G'+ general_id
    for node in sockets:
        if node.id == node_id:
            node.stop()
            sockets.remove(node)
            if node.election_status.name == 'primary':
                for node in sockets:
                    if node.id == 'G'+str(int(general_id)+1):
                        node.election_status = Election.primary
            


def is_good_entry(cmd) -> bool:
    if len(cmd) < 2:
        print("Usage: actual-order <'attack' or 'retreat'>")
        return False
    else:
        if str(cmd[1]) != "attack" and str(cmd[1]) != "retreat":
            print("Usage: actual-order <'attack' or 'retreat'>")
            return False
        else:
            return True


def get_usage():
    print("Usage: python Generals_Byzantine_program.py <number of processes>")
    sys.exit(1)





if __name__ == "__main__":
    if len(sys.argv) != 2:
        get_usage()
    else:
        start(sys.argv[1])
