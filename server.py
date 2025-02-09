import socket
import threading

# ========== Server Configuration ==========
SERVER_IP = "127.0.0.1"    # Localhost
SERVER_PORT = 5001         # Must match client port
MAX_CLIENTS = 3            # Maximum allowed connections

# ========== Global Variables ==========
connected_clients = {}      # Format: {client_socket: "Client01"}
client_counter = 0          # Tracks total clients for naming
client_counter_lock = threading.Lock()  # Prevents duplicate client numbers

# ========== Client Handling Function ==========
def handle_client(client_socket, client_address):
    global client_counter

    # Immediate server-full check
    if len(connected_clients) >= MAX_CLIENTS:
        client_socket.sendall("Server full. Try again later.".encode())
        client_socket.close()
        print(f"❌ Rejected {client_address} (server full)")
        return

    # Unique client name assignment (FIXED duplicate names issue)
    with client_counter_lock:
        client_counter += 1
        client_name = f"Client{client_counter:02}"  # Client01, Client02, etc.

    # Add to connected clients and send welcome
    connected_clients[client_socket] = client_name
    client_socket.sendall(client_name.encode())
    print(f"✅ {client_name} connected from {client_address}")

    try:
        while True:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            
            if not message:  # Client disconnected
                break
                
            print(f"{client_name} says: {message}")

            # Handle special commands
            if message.lower() == "status":
                online = ", ".join(connected_clients.values())
                client_socket.sendall(f"Online: {online}".encode())
            elif message.lower() == "exit":
                client_socket.sendall("Goodbye!".encode())
                break
            else:  # Regular message with ACK (FIXED ACK format)
                client_socket.sendall(f"{message} ACK".encode())  # Correct ACK
                
    except Exception as error:
        print(f"⚠️ Error with {client_name}: {error}")
    finally:
        # Cleanup on disconnect (FIXED connection limit enforcement)
        client_socket.close()
        del connected_clients[client_socket]
        print(f"🚪 {client_name} disconnected")

# ========== Server Setup ==========
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(MAX_CLIENTS)
print(f"🚀 Server started on {SERVER_IP}:{SERVER_PORT} (Max {MAX_CLIENTS} clients)")

# ========== Main Connection Loop ==========
try:
    while True:
        new_socket, address = server_socket.accept()
        print(f"🔗 New connection from {address}")
        
        # Start thread for simultaneous connections (FIXED threading issue)
        handler = threading.Thread(target=handle_client, args=(new_socket, address))
        handler.start()
        
except KeyboardInterrupt:
    print("\n🛑 Server shutting down...")
finally:
    server_socket.close()
    print("✅ Server closed")