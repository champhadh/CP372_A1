
import socket
import threading

# the following is the server configuration, where I defined the basic network settings and connection limits 
#the server uses 127.0.0.1 which is a localhost for local testing
# the clients must connect to the same port 5001, of which the server allows up 3 clients simutaneously.  
server_ip = "127.0.0.1"
server_port = 5001
client_cap = 3

# the following is the gloabl variables, which manages client connections and server state. 
# clients_connected stores socket-to-name mappings. the client_count gens. seq. names like Client01, Client02, et...
# and running is a flag to start or stop the server
clients_connected = {}
client_count = 0
client_count_lock = threading.Lock()
running = True  # Control server shutdown



def client_handling(client_socket, client_address):
    global client_count

    # Check server capacity
    if len(clients_connected) >= client_cap:
        client_socket.sendall(b"Server full")
        client_socket.close()
        print(f"Rejected {client_address}")
        return

    # Assign client name
    with client_count_lock:
        client_count += 1
        client_name = f"Client{client_count:02}"

    # Register client
    clients_connected[client_socket] = client_name
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
                online = ", ".join(clients_connected.values())
                client_socket.sendall(f"Online: {online}".encode())
            elif message.lower() == "exit":
                client_socket.sendall(b"Goodbye")
                active = False
            else:
                client_socket.sendall(f"{message} ACK".encode())

    # Cleanup
    client_socket.close()
    del clients_connected[client_socket]
    print(f"{client_name} disconnected")

# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(client_cap)
print(f"Server started on port {server_port}")

# Main loop
while running:
    # Accept new connections
    new_socket, address = server_socket.accept()
    
    # Check if still running
    if running:
        print(f"New connection from {address}")
        thread = threading.Thread(target=client_handling, args=(new_socket, address))
        thread.start()
    else:
        new_socket.close()

# Clean shutdown (will never reach here without external interrupt)
server_socket.close()
print("Server closed")