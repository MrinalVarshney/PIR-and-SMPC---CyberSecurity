import socket
import threading
import sys
from cryptography.fernet import Fernet

# =================================================================
# TOGGLE SWITCHES
# =================================================================

# 1. Set to False for Part 1 (Plaintext) or True for Part 2 (Encrypted)
IS_ENCRYPTED = False 

# 2. Key Source Control (Only relevant when IS_ENCRYPTED is True)
#    - True: Client waits for and uses the Server's key (Ex 2.1 & Ex 2.2 Clients 1/2)
#    - False: Client generates and uses its OWN key (Ex 2.2 Client 3 - Wrong Key Test)
USE_SERVER_KEY = False 

# =================================================================

HOST = '127.0.0.1'
PORT = 65432        # Must match server port

# Global state for key management
ENCRYPTION_KEY = None 

def encrypt_message(message):
    """Encrypts a message using the Fernet key."""
    if ENCRYPTION_KEY:
        f = Fernet(ENCRYPTION_KEY)
        return f.encrypt(message.encode('utf-8'))
    return message.encode('utf-8')

def decrypt_message(data):
    """Decrypts data using the Fernet key."""
    if ENCRYPTION_KEY:
        f = Fernet(ENCRYPTION_KEY)
        return f.decrypt(data).decode('utf-8')
    return data.decode('utf-8')

def receive_messages(client_socket):
    """Thread to continuously receive messages from the server."""
    global ENCRYPTION_KEY
    key_received = False
    
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("\n[DISCONNECTED] Server closed the connection.")
                break
            
            # --- Key Reception Logic for USE_SERVER_KEY = True ---
            if IS_ENCRYPTED and USE_SERVER_KEY and not key_received:
                # Client is configured to receive key from server.
                ENCRYPTION_KEY = data
                key_received = True
                print(f"\r[CRYPTO] Successfully received key from server.\n> ", end="", flush=True)
                continue # The key itself is not a message to display
            # ----------------------------------------------------
            
            # 1. Decrypt if required
            if IS_ENCRYPTED:
                if not ENCRYPTION_KEY:
                    print("\n[ERROR] Missing encryption key. Cannot decrypt.")
                    continue
                try:
                    message = decrypt_message(data)
                except Exception as e:
                    # Capture the expected error for Exercise 2.2
                    message = f"|ENCRYPTED DATA: {data}| - Decryption Failed: {e}" 
            else:
                # Part 1: Decode plaintext data
                message = data.decode('utf-8')

            print(f"\r{message}\n> ", end="", flush=True) 
            
        except Exception as e:
            print(f"\n[ERROR] An error occurred while receiving: {e}")
            break
    
    client_socket.close()
    sys.exit()

def send_messages(client_socket):
    """Thread to continuously send messages to the server."""
    while True:
        message = input("> ")
        if message.lower() == 'quit':
            client_socket.close()
            break
        
        # 1. Encrypt if required
        if IS_ENCRYPTED:
            # Check if key is available before sending encrypted message
            if ENCRYPTION_KEY is None:
                 print("\n[WAITING] Key not yet available. Please wait...")
                 continue
            encoded_message = encrypt_message(message)
        else:
            # Part 1: Encode plaintext
            encoded_message = message.encode('utf-8')

        try:
            client_socket.send(encoded_message)
        except:
            break

def start_client():
    global ENCRYPTION_KEY
    
    # --- Local Key Generation Logic for USE_SERVER_KEY = False ---
    if IS_ENCRYPTED and not USE_SERVER_KEY:
        ENCRYPTION_KEY = Fernet.generate_key()
        print(f"[CRYPTO] Generated OWN key for Wrong Key Test.")
    # -----------------------------------------------------------
        
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        mode = "ENCRYPTED" if IS_ENCRYPTED else "PLAINTEXT"
        print(f"[CONNECTED] Connected to {mode} chat server at {HOST}:{PORT}")
        print("Type 'quit' to exit.")
        
        threading.Thread(target=receive_messages, args=(client,)).start()
        send_messages(client) 
        
    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused. Is the server running on {HOST}:{PORT}?")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    start_client()