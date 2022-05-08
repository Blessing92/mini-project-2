import sys
import time
import random
from state import State, Election
from utilities import make_the_connections, count_generals, get_sender

from general import MyTestNode


global message
global initial_nb_of_generals
global last_used_port
message = []
sockets = []
used_ports = []
all_threads = []
actions = ['attack', 'retreat']
resources = False
count_attacks = 0
count_retreats = 0


def start(args):

    port = 10001
    number_of_processes = int(args)

    global initial_nb_of_generals
    initial_nb_of_generals = int(args)

    for node_id in range(number_of_processes):
        node = MyTestNode(host="127.0.0.1", port=port, id="G" + str(node_id+1))
        used_ports.append(port)
        port += 1
        node.start()
        sockets.append(node)
    
    # Set the last occupied port
    global last_used_port
    last_used_port = port

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
                byzantine_action(str(cmd[1]))
                actual_order()
        
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
                    print("Please wait ....")
                    kill_general(cmd[1])

        # $ g-add K, where K is the number of new generals. By default, generals have a non-faulty state once created
        elif command == "g-add":
            if len(cmd) != 2:
                print("Usage: g-add <number>")
            else:
                if not cmd[1].isnumeric():
                    print(cmd[1], " is not a valid integer")
                else:
                    add_general(int(cmd[1]))

        elif command == 'exit':
            for node in sockets:
                node.stop()
            print(
                "Program Terminated Successfully! Please wait for all the nodes to stop...")
            sys.exit()
        else:
            print("Invalid command! Please try again...")


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
                # Sort the nodes in order to elect the new Primary General
                nodes_sorted = sorted(sockets, key=lambda node: node.id)
                new_leader = nodes_sorted[0]
                new_leader.election_status = Election.primary


# $ g-add K, where K is the number of new generals. By default, generals have a non-faulty state once created
def add_general(number):
    global last_used_port, initial_nb_of_generals
    new_port = last_used_port+1
    value = number + initial_nb_of_generals

    for node_id in range(number):
        node = MyTestNode(host="127.0.0.1", port=new_port, id="G" + str(value))
        used_ports.append(new_port)
        new_port += 1
        value -= 1
        node.start()
        sockets.append(node)

    # Node 1 connect to other nodes
    make_the_connections(sockets)

    # update the last used port
    last_used_port = new_port

    # update the initial number generals
    initial_nb_of_generals = len(sockets)


# Primery general managing the the attack
def byzantine_action(action):
    # Calculate the number of generals required to take actions
    required_generals, fautly_counter = count_generals(sockets)

    for node in sockets:
        if node.election_status.name == "primary":
            node.ownMessage = []

            if node.state.name == "NF":
                # node.majority = str(action)
                if len(sockets) < required_generals:
                    node.ownMessage.append((action, node.id))
                else:
                    # Primary stores the action sent to the generals
                    node.ownMessage.append((action, node.id))
                    node.send_to_nodes(action + ", from, primary")
                    time.sleep(2)
            else:
                # node.majority = random_action
                if len(sockets) < required_generals:
                    node.ownMessage.append((action, node.id))
                else:
                    # Primary stores the action sent to the generals
                    node.ownMessage.append((action, node.id))
                    node.send_to_nodes(action + ", from, primary")
                    time.sleep(2)
  

# actual order of execution
# Execute order:
def actual_order():
    
    # Calculate the number of generals required to take actions
    required_generals, fautly_counter = count_generals(sockets)

    if len(sockets) < required_generals:
        for node in sorted(sockets, key=lambda node: node.id):
            if node.election_status.name == "primary":
                node.majority = node.ownMessage[0][0]
            else:
                node.majority = 'undefined'
        
        for node in sorted(sockets, key=lambda node: node.id):
            print(str(node.id) + ", " + str(node.election_status.name) + ", majority=" + str(node.majority) + ", state=" + str(node.state.name))
        print("Execute order: cannot be determined – not enough generals in the system! " + 
        str(fautly_counter), " faulty node in the system " + str(len(sockets) - 1) + " out of " + str(len(sockets)) + "  quorum not consistent")

    else:
        count_attacks = 0
        count_retreats = 0

        for node in sorted(sockets, key=lambda node: node.id):
            if node.election_status.name != "primary":
                attacks = 0
                retreats = 0
                for action in node.ownMessage:
                    if action[0] == "attack":
                        attacks += 1
                    else:
                        retreats += 1
                # Each node decide based on the action received 
                if attacks > retreats:
                    count_attacks += 1
                elif retreats > attacks:
                    count_retreats += 1
                else:
                    pass
        
        # The primary decide based on the quorum the votes of the generals
        if count_attacks > count_retreats:
            if fautly_counter == 0:
                for node in sorted(sockets, key=lambda node: node.id):
                    node.majority = "attack"
                for node in sorted(sockets, key=lambda node: node.id):
                    print(str(node.id) + ", " + str(node.election_status.name) + ", state=" + str(node.state.name))

                print("Execute order: " + node.majority + "! " + " Non-faulty nodes in the system - " + str(count_attacks) + " out of " + str(len(sockets)) + " quorum suggest " + node.majority)
            else:
                for node in sorted(sockets, key=lambda node: node.id):
                    node.majority = "attack"
                for node in sorted(sockets, key=lambda node: node.id):
                    print(str(node.id) + ", " + str(node.election_status.name) + ", state=" + str(node.state.name))

                print("Execute order: " + node.majority + "! " + str(fautly_counter) + " faulty node in the system - " + str(count_attacks) + " out of " + str(len(sockets)) + " quorum suggest " + node.majority)
        else:
            if fautly_counter == 0:
                for node in sorted(sockets, key=lambda node: node.id):
                    node.majority = "retreat"
                for node in sorted(sockets, key=lambda node: node.id):
                    print(str(node.id) + ", " + str(node.election_status.name) + ", state=" + str(node.state.name))

                print("Execute order: " + node.majority + "! " + "Non-faulty node in the system - " + str(count_retreats) + " out of " + str(len(sockets)) + " quorum suggest " + node.majority)
            else:
                for node in sorted(sockets, key=lambda node: node.id):
                    node.majority = "retreat"
                for node in sorted(sockets, key=lambda node: node.id):
                    print(str(node.id) + ", " + str(node.election_status.name) + ", state=" + str(node.state.name))

                print("Execute order: " + node.majority + "! " + str(fautly_counter) + " faulty node in the system - " + str(count_retreats) + " out of " + str(len(sockets)) + " quorum suggest " + node.majority)


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

def get_usage_2():
    print("Usage: number of generals must be greater than zero")
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        get_usage()
    else:
        if int(sys.argv[1]) <= 0:
            get_usage_2()
        else:
            start(sys.argv[1])
