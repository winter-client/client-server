import socket
import threading

def send_messages(client_socket):
    while True:
        message = input()
        if message == "@quit":
            client_socket.sendall(message.encode('utf-8'))
            break
        elif message == "@names":
            client_socket.sendall(message.encode('utf-8'))
        elif message.startswith('@'):
            recipient_name, message_body = message.split('@', 1)[1].split(' ', 1)
            client_socket.sendall(f"@{recipient_name} {message_body}".encode('utf-8'))
        elif message.startswith('@group set'):
            client_socket.sendall(message.encode('utf-8'))
        elif message.startswith('@group delete'):
            client_socket.sendall(message.encode('utf-8'))
        elif message.startswith('@group leave'):
            client_socket.sendall(message.encode('utf-8'))
        else:
            client_socket.sendall(message.encode('utf-8'))

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Check if the message is a personal message
                if message.startswith("[") and "(private)" in message:
                    # Extract sender's name from the message
                    sender_name = message.split()[0][1:]
                    personal_message = message.split(":", 1)[1].strip()
                    print(f"[Personal Message from {sender_name}]: {personal_message}")
                else:
                    print(message)
        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    # host = localhost / port = 8888
    host = input("Enter server IP address: ")  # Prompt user for server IP address
    port = int(input("Enter server port number: "))  # Prompt user for server port number

    while True:  # Loop for username validation
        # Receive username prompt from server
        username = input("Enter your username: ")

        # Create client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        # Send username to server
        client_socket.sendall(username.encode('utf-8'))

        # Receive validation response from server
        validation_response = client_socket.recv(1024).decode('utf-8')
        print(validation_response)

        if validation_response != "[Username has already been used. Please enter another name.]":
            break  # Break the loop if the username is valid

    # Receive welcome message from server
    welcome_message = client_socket.recv(1024).decode('utf-8')
    print(welcome_message)

    # Start thread to send messages to server
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.start()
    # Start thread to receive messages from server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

if __name__ == "__main__":
    main()
