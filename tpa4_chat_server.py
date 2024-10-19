#!env python

"""Chat server for CST311 Programming Assignment 4"""
__author__ = "[Group 4]"
__credits__ = [
    "Chris Tangonan",
    "Edward Torres",
    "Victoria Ramirez",
    "Guillermo Zendejas"
]

import socket as s
import ssl
import time
import threading

# Configure logging
import logging
from lib2to3.fixes.fix_input import context

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('/etc/ssl/demoCA/newcerts/tpa4.chat.test-cert.pem', '/etc/ssl/demoCA/private/tpa4.chat.test-key.pem')

server_port = 12000
thread_list = []
connections = []
addresses = []
pending_msgs = []
client_count = 0
client_count_max = 3
is_all_clients_exit = False
user_names = ["Client X", "Client Y", "Client Z"]

def connection_handler(connection_socket, address):
    global connections, addresses, client_count, pending_msgs, is_all_clients_exit
    receiver1 = None
    receiver2 = None

    # assign initial query to connections user_name
    # query = connection_socket.recv(1024).decode()
    # user_name = query
    # user_id = len(connections) - 1
    user_name = user_names.pop(0)

    # get all pending messages sent to current client connection
    for msg in pending_msgs:
        connection_socket.send(msg.encode())
        time.sleep(.1)

    # Initial message to other clients
    query = connection_socket.recv(1024).decode()
    print("Message from " + user_name + ": " + query)
    while query != "bye":

        # condition of only one client in the server, append all msgs to pending_msgs
        if (client_count == 1):
            pending_msgs.append(user_name + ": " + query)

        # condition of only two client in the server: send 1, append for other
        elif (client_count < client_count_max):
            if (address[0] == addresses[0][0]):
                receiver1 = connections[1]
            else:
                receiver1 = connections[0]

            # send currently connected receiver the message
            receiver1.send(str(user_name + ": " + query).encode())
            # append mesage to pending_msgs for other receiver to receive at run time
            pending_msgs.append(user_name + ": " + query)

        # condition of all three clients connnected: no appending, just sendinng
        else:
            if (address[0] == addresses[0][0]):
                receiver1 = connections[1]
                receiver2 = connections[2]
            elif (address[0] == addresses[1][0]):
                receiver1 = connections[0]
                receiver2 = connections[2]
            else:
                receiver1 = connections[0]
                receiver2 = connections[1]

            # send message to all currently addressable receivers
            receiver1.send(str(user_name + ": " + query).encode())
            receiver2.send(str(user_name + ": " + query).encode())
            pending_msgs.append(user_name + ": " + query)

        # this blocks, if no message has been received
        query = connection_socket.recv(1024).decode()
        print("Message from " + user_name + ": " + query)

    # connection close out after client says bye
    # decrement client_count, take out address, and connection_socket from associated arrays
    addresses.remove(address)
    connections.remove(connection_socket)
    client_count -= 1


    for receiver in connections:
        receiver.send(str(user_name + " has disconnected").encode())

    if client_count == 0:
        is_all_clients_exit = True

    print("INFO:___main___: " + user_name + " has left the chat.")
    print("INFO:___main___: Closing connection to " + user_name)
    # Close client socket
    connection_socket.close()


def main():
    global connections, addresses, client_count, exitServer
    # Create a TCP socket
    # Notice the use of SOCK_STREAM for TCP packets
    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)




    # Assign port number to socket, and bind to chosen port
    server_socket.bind(('', server_port))

    # Configure how many requests can be queued on the server at once
    server_socket.listen(client_count_max)
    ssock = context.wrap_socket(server_socket, server_side=True)

    # Alert user we are now online
    log.info("The server is ready to receive on port " + str(server_port))

    # Surround with a try-finally to ensure we clean up the socket after we're done
    try:
        # Enter forever loop to listen for requests
        for i in range(client_count_max):
            # When a client connects, create a new socket and record their address

            connection_socket, address = ssock.accept()
            client_count += 1
            connections.append(connection_socket)
            addresses.append(address)

            log.info("Connected to client at " + str(address) + "\nconnection_socket: " + str(connection_socket))

            # TODO: Determine if address has already visited server

            # Pass the new socket and address off to a connection handler function
            # connection_handler(connection_socket, address)

            # implementation of threading
            t = threading.Thread(target=connection_handler, args=(connection_socket, address))

            # starts thread, which initiates connection_handler function for the current client connected.
            t.start()

            # append thread to thread list
            thread_list.append(t)
    finally:
        for t in thread_list:
            t.join()
        server_socket.close()

        # joins the existing threads in thread_list


if __name__ == "__main__":
    main()



