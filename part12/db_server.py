import socket
import threading
from datetime import datetime

HOST = '127.0.0.1'
PORT = 54321  # DB Server Port

# 1. Server hosts 50 records (key-value pairs)
DATABASE = {i: f"Record Data for ID: {i}. This is highly sensitive information." 
            for i in range(1, 51)}
LOG_FILE = "server_log.txt"

def log_query(record_id, client_address):
    """Logs the record ID, client IP, and timestamp to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Client IP: {client_address[0]}:{client_address[1]}, Requested Record ID: {record_id}\n"
    print(f"[LOG] {log_entry.strip()}")
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def handle_query(client_socket, client_address):
    """Handles a single client query in a thread."""
    print(f"[NEW CONNECTION] DB Client {client_address} connected.")
    try:
        data = client_socket.recv(1024)
        if data:
            record_id_str = data.decode('utf-8').strip()
            try:
                record_id = int(record_id_str)
                
                # Log the request as required
                log_query(record_id, client_address)
                
                # Fetch and send the record back (plaintext)
                if record_id in DATABASE:
                    record = DATABASE[record_id]
                    response = f"SUCCESS: {record}"
                else:
                    response = "ERROR: Invalid Record ID."

            except ValueError:
                response = "ERROR: Request must be a valid integer ID."

            client_socket.sendall(response.encode('utf-8'))
            
    except:
        pass
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] DB Client {client_address} closed.")

def start_db_server():
    """Sets up the DB server socket and listens for queries."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5) 
    print(f"[LISTENING] DB Server is listening on {HOST}:{PORT}")
    
    # Initialize the log file
    with open(LOG_FILE, "w") as f:
        f.write(f"--- DB Server Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    while True:
        client_socket, client_address = server.accept() 
        thread = threading.Thread(target=handle_query, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_db_server()
