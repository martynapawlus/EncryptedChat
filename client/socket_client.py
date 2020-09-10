import socket
from threading import Thread
import encription

HEADER_LENGTH = 10
client_socket = None


# Connecting with the server method
def connect(ip, port, my_username, public_key, error_callback):

    global client_socket
    # Creating socket with IPv4 and TCP connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connecting to a given ip and port
        client_socket.connect((ip, port))
    except Exception as e:
        # Connection error
        error_callback('Connection error: {}'.format(str(e)))
        return False

    # Encoding username to bytes, then counting number of bytes and preparing header of a fixed sized
    # Username header is an encoded username with the length of HEADER_LENGTH
    # Message_flag - k for key distribution
    flag = "k".encode('utf-8')
    username = my_username.encode('utf-8')
    public_key = public_key.encode('utf-8')
    connection_data = flag + public_key + username
    connection_header = f"{len(connection_data):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(connection_header + connection_data)
    return True


# Sending a message to the server method
def send(flag, message):
    # Encoding message the same way as username above
    message = (flag + message).encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    # friend_username = friend_username.encode('utf-8')
    client_socket.send(message_header + message)


# Method that invokes listening function in a thread
def start_listening(incoming_message_callback, error_callback):
    Thread(target=listen, args=(incoming_message_callback, error_callback), daemon=True).start()


# Listening for incoming messages
def listen(incoming_message_callback, error_callback):
    while True:

        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data
                if not len(username_header):
                    error_callback('Connection closed by the server')

                # Converting header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receiving and decode username
                username = client_socket.recv(username_length).decode('utf-8')[6:]

                with open("prev_details.txt", "r") as f:
                    d = f.read().split(":")
                    my_username = d[2]

                # Now do the same for message
                # As we received username, we received whole message, there's no need to check if it has any length
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                print("Username " + username)
                print("My_username " + my_username)

                if message[0] == "p" and username == my_username:

                    with open("my_keys.txt", "r") as f:
                        d = f.read().split(":")
                        public_key = int(d[0])
                        private_key = int(d[1])

                    d = message[1:].split(":")
                    temp_friend_username = d[0]
                    temp_friend_key = int(d[1])

                    with open("public_keys.txt", 'a') as f:
                        f.write('%s:%s\n' % (temp_friend_username, str(temp_friend_key)))

                    temp_key = encription.generate_temporary_key(public_key, temp_friend_key, private_key)
                    message = str(temp_key) + ":" + temp_friend_username + ":" + str(public_key)
                    flag = "t"
                    send(flag, message)

                elif message[0] == "s":
                    print("i get it ")
                    d = message[1:].split(":")
                    temporary_key = int(d[0])
                    receiver_username = d[1]

                    if my_username == receiver_username:
                        with open("my_keys.txt", "r") as f:
                            d = f.read().split(":")
                            my_private_key = int(d[1])

                        username_key = {}
                        with open("public_keys.txt") as raw_data:
                            for item in raw_data:
                                if ':' in item:
                                    current_username, current_key = item.split(':', 1)
                                    username_key[current_username] = current_key
                                    print(current_key)

                        friend_key = int(username_key[username])

                        print("eluwina")
                        symmetric_key = encription.generate_symmetric_key(temporary_key, friend_key, my_private_key)

                        with open("symmetric_keys.txt", "a") as f:
                            f.write(f"{username}:{symmetric_key}\n")

                elif message[0] == "t":
                    print("i get it ")
                    d = message[1:].split(":")
                    temporary_key = int(d[0])
                    receiver_username = d[1]
                    friend_key = int(d[2])

                    if my_username == receiver_username:
                        with open("public_keys.txt", 'a') as f:
                            f.write('%s:%s\n' % (username, str(friend_key)))

                        with open("my_keys.txt", "r") as f:
                            d = f.read().split(":")
                            my_public_key = int(d[0])
                            my_private_key = int(d[1])

                        print("eluwina")
                        symmetric_key = encription.generate_symmetric_key(temporary_key, my_public_key, my_private_key)

                        with open("symmetric_keys.txt", "a") as f:
                            f.write(f"{username}:{symmetric_key}\n")

                        my_temp_key = encription.generate_temporary_key(friend_key, my_public_key, my_private_key)
                        key_message = str(my_temp_key) + ":" + username
                        flag = "s"
                        send(flag, key_message)

                elif message[0] == "m":
                    # Print message
                    incoming_message_callback(username, message[1:])

                elif message[0] == "e":
                    # Print message
                    friend_username = username
                    d = message[1:].split(":")
                    receiver_username = d[0]
                    encrypted_message = d[1]

                    if receiver_username == my_username:
                        username_symmetric_key = {}
                        with open("symmetric_keys.txt") as raw_data:
                            for item in raw_data:
                                if ':' in item:
                                    current_username, current_symmetric_key = item.split(':', 1)
                                    username_symmetric_key[current_username] = current_symmetric_key

                        if friend_username in username_symmetric_key:

                            symmetric_key = int(username_symmetric_key[friend_username])

                            # Get message text and clear message input field

                            encrypted_message = encription.decrypt_message(encrypted_message, symmetric_key)
                            print("odkodowana: " + encrypted_message)

                    incoming_message_callback(username, encrypted_message)

        except Exception as e:
            # Any other exception - something happened, exit
            error_callback('Reading error: {}'.format(str(e)))

