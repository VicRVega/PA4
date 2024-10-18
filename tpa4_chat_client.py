"""Chat client for CST311 Programming Assignment 4"""
__author__ = "[Group 4]"
__credits__ = [
    "Chris Tangonan",
    "Edward Torres",
    "Victoria Ramirez",
    "Guillermo Zendejas"
]

# Import statements
import socket as s
import threading

# Configure logging
import logging
import os

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Set global variables
server_name = '10.0.2.3'  # IP of h4
server_port = 12000


def incoming_message_handler(client_socket):
    while True:
        try:
            incoming_message = client_socket.recv(1024)
            if incoming_message:
                print(incoming_message.decode())
            else:
                break
        except:
            break


def main():
    # Create socket
    client_socket = s.socket(s.AF_INET, s.SOCK_STREAM)

    t = threading.Thread(target=incoming_message_handler, args=(client_socket,))
    t.start()
    try:
        # Establish TCP connection
        client_socket.connect((server_name, server_port))
    except Exception as e:
        log.exception(e)
        log.error("***Advice:***")
        if isinstance(e, s.gaierror):
            log.error("\tCheck that server_name and server_port are set correctly.")
        elif isinstance(e, ConnectionRefusedError):
            log.error("\tCheck that server is running and the address is correct")
        else:
            log.error("\tNo specific advice, please contact teaching staff and include text of error and code.")
        exit(8)

    # Get input from user
    user_input = input('Welcome to the chat! To send a message, type the message and click enter.\n')

    try:
        # keep the connection open as long as the message is not 'bye'
        while user_input != 'bye':
            # Set data across socket to server
            #  Note: encode() converts the string to UTF-8 for transmission
            client_socket.send(user_input.encode())

            # Get input from user
            user_input = input()

    finally:
        # set user_input to 'bye' so server recieves final message
        user_input = 'bye'
        # Set data across socket to server
        #  Note: encode() converts the string to UTF-8 for transmission
        client_socket.send(user_input.encode())
        # Close socket prior to exit
        client_socket.close()
        os.system("clear")
        t.join()


# This helps shield code from running when we import the module
if __name__ == "__main__":
    main()
