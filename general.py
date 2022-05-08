import time
import random
from node import Node
from state import State, Election


actions = ['attack', 'retreat']
message = []


class MyTestNode (Node):
    def __init__(self, host, port, id):
        self.ownMessage = []
        self.timestamp = 0
        self.state = State.NF
        self.majority = ""
        self.election_status = Election.secondary
        self.local_count = 0
        self.queues = []

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

        # When we receive data from the primary with new action, we reset our local storage
        get_received = str(data.split(",")[2])
        received_from = get_received.strip()

        if received_from == "primary":
            self.ownMessage = []
            
            if self.state.name == 'NF':
                action = str(data.split(",")[0])
                self.ownMessage.append((action, node.id))
              
                # Send the new action to other generals except the "Primary General"
                forward_action = action + ", from, " + str(self.id)
                self.send_to_nodes(forward_action, exclude=[node])
                time.sleep(2)
            else:
                action = str(data.split(",")[0])
                random_action = random.choice(actions)
                self.ownMessage.append((action, node.id))

                # Send the new action to other generals except the "Primary General"
                forward_action = random_action + ", from, " + str(self.id)
                self.send_to_nodes(forward_action, exclude=[node])
                time.sleep(2)

        else:
            action = str(data.split(",")[0])
            self.ownMessage.append((action, node.id))
              
          
 

    def node_disconnect_with_outbound_node(self, node):
        global message
        message.append(
            "node wants to disconnect with oher outbound node: " + node.id)

    def node_request_to_stop(self):
        global message
        message.append("node is requested to stop!")