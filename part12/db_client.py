import socket
import sys

HOST = '127.0.0.1'
PORT = 54321  # Must match server port

def start_client(record_id):
    """Connects to the server, sends the record ID, and prints the result."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        print(f"[CONNECTED] Requesting record ID #{record_id}...")
        
        # Send the record ID in plaintext
        client.sendall(str(record_id).encode('utf-8'))
        
        # Receive the response in plaintext
        data = client.recv(1024)
        response = data.decode('utf-8')
        
        print(f"[SERVER RESPONSE]: {response}")
        
    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused. Is the database server running on {HOST}:{PORT}?")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python db_client.py <record_id>")
        print("Example: python db_client.py 15")
        sys.exit(1)
        
    try:
        record_id = int(sys.argv[1])
        start_client(record_id)
    except ValueError:
        print("Error: Record ID must be an integer.")
        sys.exit(1)
