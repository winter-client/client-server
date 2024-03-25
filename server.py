import socket
import threading
import signal
import sys

# Define a global variable to track whether the server is running
server_running = True

# Define a signal handler function to gracefully shutdown the server
def signal_handler(sig, frame):
    print('Shutting down server...')
    global server_running
    server_running = False
    sys.exit(0)

# Main function to handle client connections
def handle_client(client_socket, clients, client_names, groups):
    disconnected = False  # Flag to track if client has already been disconnected
    while not disconnected:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Broadcast message to all clients
                if message.startswith('@'):
                    handle_special_command(client_socket, clients, client_names, groups, message)
                else:
                    broadcast_message(client_socket, clients, client_names, message)
        except Exception as e:
            print(f"Error: {e}")
            disconnected = True  # Set the flag to True if an exception occurs

    # If client is still in the list, remove it and close connection
    if client_socket in clients:
        clients.remove(client_socket)
        client_socket.close()
        del client_names[client_socket]

# Function to handle special commands from client
def handle_special_command(client_socket, clients, client_names, groups, message):
    if message == '@quit':
        quit_message = f"[{client_names[client_socket]} exited]"
        broadcast_message(client_socket, clients, client_names, quit_message)
        clients.remove(client_socket)
        client_socket.close()
        del client_names[client_socket]
    elif message == '@names':
        names_message = f"[Connected users: {', '.join(client_names.values())}]"
        client_socket.sendall(names_message.encode('utf-8'))
    elif message.startswith('@group set'):
        group_command = message.split()
        if len(group_command) >= 4:
            group_name = group_command[2]
            group_members = group_command[3:]
            create_group(client_socket, client_names, groups, group_name, group_members)
        else:
            client_socket.sendall("[Invalid group set command]".encode('utf-8'))
    elif message.startswith('@group delete'):
        group_name = message.split()[2]
        delete_group(client_socket, client_names, groups, group_name)
    elif message.startswith('@group leave'):
        group_name = message.split()[2]
        leave_group(client_socket, client_names, groups, group_name)
    elif message.startswith('@group send'):
        group_message = message.split(' ', 2)[2]
        send_group_message(client_socket, client_names, groups, group_message)
    elif message.startswith('@'):
        recipient_name, message_body = message.split('@', 1)[1].split(' ', 1)
        recipient_socket = find_client_socket_by_name(client_names, recipient_name)
        if recipient_socket:
            personal_message = f"[{client_names[client_socket]} (private)]: {message_body}"
            recipient_socket.sendall(personal_message.encode('utf-8'))
        else:
            client_socket.sendall("[User not found]".encode('utf-8'))
    else:
        broadcast_message(client_socket, clients, client_names, message)

# Function to create a group
def create_group(client_socket, client_names, groups, group_name, group_members):
    if group_name.isalnum() and group_name not in groups:
        groups[group_name] = group_members
        client_socket.sendall(f"[You are enrolled in the {group_name} group]".encode('utf-8'))
        for member in group_members:
            member_socket = find_client_socket_by_name(client_names, member)
            if member_socket:
                member_socket.sendall(f"[You are enrolled in the {group_name} group]".encode('utf-8'))
    else:
        client_socket.sendall("[Invalid group name or group already exists]".encode('utf-8'))

# Function to delete a group
def delete_group(client_socket, client_names, groups, group_name):
    if group_name in groups:
        del groups[group_name]
        client_socket.sendall(f"[Group {group_name} deleted]".encode('utf-8'))
    else:
        client_socket.sendall("[Group not found]".encode('utf-8'))

# Function to leave a group
def leave_group(client_socket, client_names, groups, group_name):
    if group_name in groups and client_names[client_socket] in groups[group_name]:
        groups[group_name].remove(client_names[client_socket])
        client_socket.sendall(f"[You left the {group_name} group]".encode('utf-8'))
    else:
        client_socket.sendall("[You are not in this group]".encode('utf-8'))

# Function to send a message to a group
def send_group_message(client_socket, client_names, groups, message):
    for group_name, group_members in groups.items():
        if client_names[client_socket] in group_members:
            for member_name in group_members:
                member_socket = find_client_socket_by_name(client_names, member_name)
                if member_socket:
                    member_socket.sendall(f"[{client_names[client_socket]} (group)]: {message}".encode('utf-8'))

# Function to send messages to all other clients
def broadcast_message(sender_socket, clients, client_names, message):
    for client_socket in clients:
        if client_socket != sender_socket:
            username = client_names[sender_socket]
            client_socket.sendall(f"[{username}]: {message}".encode('utf-8'))

# Function to obtain target client socket
def find_client_socket_by_name(client_names, name):
    for client_socket, username in client_names.items():
        if username == name:
            return client_socket
    return None

def main():
    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Server configuration
    host = 'localhost'
    port = 8888

    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[*] Listening on {host}:{port}")

    clients = []
    client_names = {}
    groups = {}

    while server_running:  # Loop until server_running is False
        # Accept client connection
        client_socket, addr = server_socket.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        # Prompt client for username
        client_socket.sendall("[Enter your username:]".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()
        # Check if Username has been taken
        while username in client_names.values():
            client_socket.sendall("[Username has already been used. Please enter another name:]".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8').strip()

        client_names[client_socket] = username
        # Welcome Message to Client
        welcome_message = f"[Welcome {username}!]"
        client_socket.sendall(welcome_message.encode('utf-8'))

        # Broadcast to other clients
        joined_message = f"[{username} joined]"
        for client in clients:
            if client != client_socket:
                client.sendall(joined_message.encode('utf-8'))

        # Add client to list
        clients.append(client_socket)

        # Create thread to handle client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients, client_names, groups))
        client_thread.start()

    # Close the server socket when the server stops running
    server_socket.close()

if __name__ == "__main__":
    main()