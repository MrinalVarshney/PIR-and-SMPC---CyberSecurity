import socket
import threading

HOST = '127.0.0.1'
PORT = 65432        # Chat Server Port

# List to keep track of connected clients
clients = []

def broadcast(message, client_socket):
    """Sends a message to all connected clients except the sender."""
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                # Remove disconnected clients
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client_socket, client_address):
    """Handles communication with a single client in a separate thread."""
    print(f"[NEW CONNECTION] {client_address} connected.")
    clients.append(client_socket)
    
    # Send a welcome message
    welcome_message = f"You are connected! Your port is {client_address[1]}"
    client_socket.send(welcome_message.encode('utf-8'))

    try:
        while True:
            # Receive up to 1024 bytes of data
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8')
            print(f"[{client_address[1]}] sent: {message}")
            
            # Broadcast the message
            broadcast_message = f"Client {client_address[1]}: {message}"
            broadcast(broadcast_message, client_socket)
            
    except:
        pass # Handle connection loss gracefully
    finally:
        # Clean up the connection
        if client_socket in clients:
            clients.remove(client_socket)
        client_socket.close()
        print(f"[DISCONNECTED] {client_address} closed.")

def start_server():
    """Sets up and runs the server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(3) # Max 3 simultaneous clients as per lab environment setup
    print(f"[LISTENING] Chat Server is listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept() 
        # Start a new thread for each client
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
