import time


def extra_data(data):
    data = data.split(" ")
    event = data[0]
    sender_id = data[1]
    timestamp = data[2]
    port = data[3]

    return event, sender_id, timestamp,port   

def build_data(event, node_id, timestamp, port):
    data = str(event) + " " + str(node_id) + " " + str(timestamp) + " " + str(port)
    return data


check = []

def checker(el):
    for i in check:
        temp = i.split(",")
        new = temp[1] + "," + temp[0]
        if new == el:
            return False
        
    return True



def make_the_connections(sockets):
    for node_i in sorted(sockets, key=lambda node: node.id):
        for node_j in sorted(sockets, key=lambda node: node.id):
            if node_i.id != node_j.id:
                is_not_already_connected = checker(str(node_i) + "," + str(node_j))
                if is_not_already_connected:
                    print("connecting node", node_i, " to ", node_j)
                    node_i.connect_with_node('127.0.0.1', node_j.port)
                    time.sleep(2)
                    check.append(str(node_i) + "," + str(node_j))

