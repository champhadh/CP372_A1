import socket
import threading

# server configuration
SERVER_HOST = "127.0.0.1"  # localhost
SERVER_PORT = 5000  # must match the client's port
max_number_clients = 3  # limit to 3 clients

# data storage
clients = {}  # stores connected clients {client_socket: "Client01", ...}
client_count = 0  # tracks the number of connected clients

# function to handle each client
def handle_client(client_socket, client_address):
    global client_count

    # if the server is full, reject the client
    if len(clients) >= max_number_clients:
        client_socket.sendall("server is full, please try again later.".encode())
        client_socket.close()
        print(f"connection rejected from {client_address} due to server being full ")
        return

    # assign a unique client name
    client_count += 1
    client_name = f"Client{client_count:02}"  # generates Client01, Client02, Client03...
    clients[client_socket] = client_name

    # send assigned client name to the client
    client_socket.sendall(client_name.encode())
    print(f"assigned {client_name} to {client_address}")

    while True:
        try:
            # receive message from the client
            message = client_socket.recv(1024).decode()
            if not message:
                break  # if client disconnects, exit the loop
            
            print(f"{client_name} sent: {message}")

            # handle special commands
            if message.lower() == "status":
                # send a list of connected clients
                status_msg = "connected clients: " + ", ".join(clients.values())
                client_socket.sendall(status_msg.encode())
            elif message.lower() == "exit":
                print(f"👋 {client_name} disconnected.")
                break
            else:
                # echo message with "ACK"
                client_socket.sendall(f"{message} ACK".encode())

        except Exception as e:
            print(f"error handling {client_name}: {e}")
            break

    # remove the client from the list and close connection
    del clients[client_socket]
    client_count -= 1
    client_socket.close()
    print(f"🔒 {client_name} connection closed.")

# providing server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(max_number_clients)
print(f"server started on {SERVER_HOST}:{SERVER_PORT} (max {max_number_clients} clients)")

while True:
    if len(clients) < max_number_clients:
        client_socket, client_address = server_socket.accept()
        print(f"connection received from {client_address}")

        # start a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
    else:
        # reject new connections if limit is reached
        rejected_socket, rejected_address = server_socket.accept()
        rejected_socket.sendall("server full. try again later.".encode())
        rejected_socket.close()
        print(f"connection rejected from {rejected_address} (server full)")
