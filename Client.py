#Arren Haroutunian - 210603250
#Hady Wehbe - 210457330


#socket is in escence part of pythons library and is used to make network connections
import socket  

"""
The 127.0.0.1 is a sepcial IP that basically means local host,
what this means is that client will connect to server running
on the local computer, 

Port number needs to match the one on Servey.py that
it can connect to the server.
"""
HOST = "127.0.0.1"  
PORT = 5001  



"""
Here we are basically creating a new socket object,
use .AF_INET to tell python that we are using
iPv4 address, and lastly socket.SOCK_STREAM tells
python that we are using TCP.
"""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect = sock.connect_ex((HOST, PORT))

#Checking if connection to server was successful
if connect == 0:
    print("You are now successfuly connected to the server!!!")
    
    #Receiving the name of the client assigned from the server
    clients_name = sock.recv(1024).decode()
    print(f"The following client name was assigned : {clients_name}")
    
    #Helper for the loop
    running = 1
    
    
    while running:
        #Gets message from the user
        users_message = input("Please enter a message or simply type 'exit' or 'status' to see list of connected clients: ")
        
        #Conditions to check if users message is not empty
        if users_message:
            sock.sendall(users_message.encode())
            
            #Checks if user inputed exit, uses lower so that any caps would accept
            if users_message.lower() == "exit":
                print("Exiting/disconnecting from the server")
                running = 0
            else:
                #receiving the users response and prints it
                users_response = sock.recv(1024).decode()
                print(f"Response from the server: {users_response}")
        else:
            print("Your message, can't be empty, please try again")
else:
    print("Failure to connect to the server, it may not be running or does not exist!!!")  

#Closes the connection socket and the loop ends
sock.close()
print("Connection is now closed.")

