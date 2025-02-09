import socket  # Used for network communication

# Define server connection details
SERVER_HOST = "127.0.0.1"  # Localhost (same machine)
SERVER_PORT = 5000         # Port number (must match the server)

# Create a TCP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Step 1: Connect to the server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("✅ Connected to the server.")

    # Step 2: Receive assigned client name from the server
    client_name = client_socket.recv(1024).decode()  # Server assigns name
    print(f"🤖 Assigned client name: {client_name}")

    # Step 3: Message loop (sending & receiving messages)
    while True:
        message = input("You: ")  # Get user input

        # Send the message to the server
        client_socket.sendall(message.encode())

        # Handle "exit" command
        if message.lower() == "exit":
            print("🔌 Disconnecting from server...")
            break  # Exit loop
        
        # Receive server response
        server_response = client_socket.recv(1024).decode()
        print(f"Server: {server_response}")

except ConnectionRefusedError:
    print("❌ Server is not running. Please start the server first.")
    exit()
except Exception as e:
    print(f"⚠️ Connection error: {e}")

# Step 4: Close the connection
finally:
    client_socket.close()
    print("✅ Connection closed.")
    


