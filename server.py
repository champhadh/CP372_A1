# the following is the server configuration, the server runs locally. it must match the client's port 
# for sccessfull connection of which ensuring the server limits active client to 3.
import socket
import threading

# the following is the global variables, which manages client connections and naming. 
# the client_counter generates seq. names (client01, client02...) Capable of tracking the total clients for naming
# the client_counter_lock ensures to prevent race conditions when incrementing the counter. 
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001
MAX_CLIENTS = 3

# Global Variables
connected_clients = {}
client_counter = 0
client_counter_lock = threading.Lock()
running = True  # Control server shutdown

def handle_client(client_socket, client_address):
    global client_counter

    # Check server capacity
    if len(connected_clients) >= MAX_CLIENTS:
        client_socket.sendall(b"Server full")
        client_socket.close()
        print(f"Rejected {client_address}")
        return

    # Assign client name
    with client_counter_lock:
        client_counter += 1
        client_name = f"Client{client_counter:02}"

    # Register client
    connected_clients[client_socket] = client_name
    client_socket.sendall(client_name.encode())
    print(f"{client_name} connected")

    # Message handling loop
    active = True
    while active:
        message = client_socket.recv(1024).decode()
        
        if not message:  # Client disconnect
            active = False
        else:
            print(f"{client_name}: {message}")

            if message.lower() == "status":
                online = ", ".join(connected_clients.values())
                client_socket.sendall(f"Online: {online}".encode())
            elif message.lower() == "exit":
                client_socket.sendall(b"Goodbye")
                active = False
            else:
                client_socket.sendall(f"{message} ACK".encode())

    # Cleanup
    client_socket.close()
    del connected_clients[client_socket]
    print(f"{client_name} disconnected")

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_CLIENTS)
print(f"Server started on port {SERVER_PORT}")

# Main loop
while running:
    # Accept new connections
    new_socket, address = server_socket.accept()
    
    # Check if still running
    if running:
        print(f"New connection from {address}")
        thread = threading.Thread(target=handle_client, args=(new_socket, address))
        thread.start()
    else:
        new_socket.close()

# Clean shutdown (will never reach here without external interrupt)
server_socket.close()
print("Server closed")