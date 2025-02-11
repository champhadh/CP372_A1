#Arren Haroutunian - 210603250
#Hady Wehbe - 210457330



import socket
import threading

# the following is the server configuration, where I defined the basic network settings and connection limits 
# the server uses 127.0.0.1 which is a localhost for local testing
# the clients must connect to the same port 5001, of which the server allows up 3 clients simutaneously.  
server_ip = "127.0.0.1"
server_port = 5001
client_cap = 3

# the following is the gloabl variables, which manages client connections and server state. 
# clients_connected stores socket-to-name mappings. the client_count gens. seq. names like Client01, Client02, et...
# and running is a flag to start or stop the server
clients_connected = {}
available_client_numbers = set(range(1, client_cap + 1)) #ensures not keep client count right when client disconnects
client_count_lock = threading.Lock()
running = True  

# the following is the client handling function, of which rejects new clients if the server is at cap
def client_handling(client_socket, client_address):
    global client_count

    # checks if server is full
    # sends a "the server is full" message to reject clients and also closes the socket immediately to free resources 
    if len(clients_connected) >= client_cap:
        client_socket.sendall(b"the server is full")
        client_socket.close()
        print(f"rejected {client_address}")
        return

    # gens a uniqe client name, ensures each client gets a unique name
    # client_count_lock, prevents duplicate numbering in multi-threaded code. 
    # the :02 format pads numbers with leading zero, e.g. Client03
    with client_count_lock:
        client_num = min(available_client_numbers)
        available_client_numbers.remove(client_num)
        client_name = f"client{client_num:02}"


    # register client and send name, which adds the client to the active list and sends their name
    # the client receives its name immediately after connecting 
    clients_connected[client_socket] = client_name
    client_socket.sendall(client_name.encode())
    print(f"{client_name} connected")

    # the following is a message handling loop, which porcesses client commands and messages 
    # status returns a list of connected clients, e.g. online: client01, client02
    # exit ensures the connection gracefully 
    # other messages inlcudes the server echoes back the message with "ACK" appended
    active = True
    while active:
        message = client_socket.recv(1024).decode()
        
        if not message:  # where the client disconnects 
            active = False
        else:
            print(f"{client_name}: {message}")
            
            # handles "status" command 

            if message.lower() == "status":
                online = ", ".join(clients_connected.values())
                client_socket.sendall(f"Online: {online}".encode())
            elif message.lower() == "exit":
                client_socket.sendall(b"Goodbye")
                active = False
            else:
                client_socket.sendall(f"{message} ACK".encode())

    # the following is a cleanup on disconnect, which releases resources when a client disconnects 
    # the client's socket is closed, the client is removed from the active lsit.
    client_socket.close() 
    
    # when a client disconnects, their number is added back to ava_client_number allowing it to be reassigned to a new client
    with client_count_lock:
        del clients_connected[client_socket]
        available_client_numbers.add(int(client_name[-2:]))
    print(f"{client_name} disconnected") 

# the server setup, which is prepares the server to accept connections (initialize the server)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.bind((server_ip, server_port))
server_socket.listen(client_cap)
print(f"server started on port {server_port}")

# the following is the main loop to accept clients, which accpets new clients and starts threads for them
# the following code server_socket.accept() waits for new connections. a new handles each client to allow simultaneous connections
# if running is False, new connections are rejected 
while running:
    # accept new connections
    new_socket, address = server_socket.accept()
    
    # check if still running
    if running:
        print(f"new connection from {address}")
        thread = threading.Thread(target=client_handling, args=(new_socket, address))
        thread.start()
    else:
        new_socket.close()

# the followng is a clean shutdown (will never reach here without external interrupt)
server_socket.close()
print("server closed")