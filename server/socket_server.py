import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Creating socket with IPv4 and TCP connection
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Binding, so server informs operating system that it's going to use given IP and port
server_socket.bind((IP, PORT))

# Server listening for new connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients - socket as a key, user header and username as data
clients = {}

key_length = 256
username_key = {}

print(f'Listening for connections on {IP}:{PORT}...')


# Handles message receiving
def receive_message(client_socket):

    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client closed a connection
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False


while True:

    # Calls Unix select() system call or Windows select() WinSock call with three parameters:
    #   - rlist - sockets to be monitored for incoming data
    #   - wlist - sockets for data to be send to (checks if for example buffers are not full and socket is ready to send some data)
    #   - xlist - sockets to be monitored for exceptions (we want to monitor all sockets for errors, so we can use rlist)
    # Returns lists:
    #   - reading - sockets we received some data on (that way we don't have to check sockets manually)
    #   - writing - sockets ready for data to be send thru them
    #   - errors  - sockets with some exceptions
    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accepting new connection
            # That gives us new socket - client socket, connected to this given client only
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            free_username = True

            current_flag = user['data'].decode('utf-8')[:1]
            current_username = user['data'].decode('utf-8')[6:]
            current_key = user['data'].decode('utf-8')[1:6]

            for check_socket in clients:
                if current_username == clients[check_socket]["data"].decode('utf-8')[6:]:
                    print('Rejecting connection, username: ' + current_username + ' is already used.')
                    free_username = False
                    client_socket.close()

            if free_username:
                # Add accepted socket to select.select() list
                sockets_list.append(client_socket)

                # Also save username and username header
                clients[client_socket] = user
                username_key[current_username] = current_key

                with open("public_keys.txt", 'a') as f:
                    for current_username, current_key in username_key.items():
                        f.write('%s:%s\n' % (current_username, current_key))
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, current_username))

        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')[6:]))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                # Remove from our list of users
                del clients[notified_socket]

                continue

            text_message = message["data"].decode("utf-8")

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]

            if text_message[0] == "q":

                with open("public_keys.txt") as raw_data:
                    for item in raw_data:
                        if ':' in item:
                            current_username, current_key = item.split(':', 1)
                            username_key[current_username] = current_key

                friend_key = username_key[text_message[1:]]
                message["data"] = ("p" + text_message[1:] + ":" + friend_key).encode("utf-8")
                message["header"] = f"{len(message['data']):<{HEADER_LENGTH}}".encode('utf-8')

                if client_socket == notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            print(f'Received message from {user["data"].decode("utf-8")[6:]}: {message["data"].decode("utf-8")}')

            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:

                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:

        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]

