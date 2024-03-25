# Socket Programming: Developing a Chat Application Using Python

This is a simple chat application developed using socket programming in Python. It allows multiple clients to connect to a server and exchange messages in real-time.

## Features

- Connect multiple clients to a single server.
- Exchange messages between clients via the server.
- Special commands such as `@quit`, `@names`, and personal messages (`@username message`).
- Group functionalities: create groups, send messages to groups, leave groups, and delete groups.

## Prerequisites

- Python 3.x installed on your system.

## Usage

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/winter-client/client-server.git
    ```

2. Navigate to the project directory:

    ```bash
    cd your-preferred-directory
    ```

3. Run the server:

    ```bash
    python server.py
    ```

4. Run the client:

    ```bash
    python client.py
    ```

5. Enter the server IP address (localhost), port number (8888), and username when prompted. 


6. Start chatting!

## Commands

- `@quit`: Quit the chat application.
- `@names`: Get the list of connected users.
- `@username message`: Send a personal message to a specific user.
- `@group set group_name user1 user2 ...`: Create a group with specified users.
- `@group delete group_name`: Delete a group.
- `@group leave group_name`: Leave a group.
- `@group send group_name message`: Send a message to a group.

## Contributing

Contributions are welcome! If you have any suggestions, improvements, or bug fixes, feel free to open an issue or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
