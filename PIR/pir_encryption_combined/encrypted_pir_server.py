import socket
import json
from cryptography.fernet import Fernet
import time

# Create dummy database
database = [{"id": i, "data": f"Record_{i}_data"} for i in range(1, 51)]

HOST = '127.0.0.1'
PORT = 65433

# Generate key (share this with the client before running)
key = Fernet.generate_key()
cipher = Fernet(key)
print(f"[SERVER] Encryption Key (share with client): {key.decode()}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("[SERVER] Waiting for encrypted connection...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\n[SERVER] Connected by {addr}")
            request = conn.recv(1024).decode()

            if request == "ENCRYPTED_FULL_DB":
                print("[SERVER] Log: encrypted full database requested")
                start = time.time()
                data = json.dumps(database).encode()
                encrypted_data = cipher.encrypt(data)
                conn.sendall(encrypted_data)
                end = time.time()
                print(f"[SERVER] Sent {len(encrypted_data)} bytes (encrypted) in {round((end - start) * 1000, 2)} ms")

            elif request.startswith("ENCRYPTED_RECORD_"):
                record_id = int(request.split("_")[-1])
                record = next((r for r in database if r["id"] == record_id), None)
                if record:
                    print(f"[SERVER] Encrypted standard query for record {record_id}")
                    data = json.dumps(record).encode()
                    encrypted_data = cipher.encrypt(data)
                    conn.sendall(encrypted_data)
                else:
                    conn.sendall(cipher.encrypt(b"Record not found"))
            else:
                conn.sendall(cipher.encrypt(b"Invalid request"))
