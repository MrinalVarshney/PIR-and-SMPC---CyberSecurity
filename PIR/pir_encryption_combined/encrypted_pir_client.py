import socket
import json
from cryptography.fernet import Fernet
import time

HOST = '127.0.0.1'
PORT = 65433

# Enter key shared by server
key = input("Enter encryption key from server: ").encode()
cipher = Fernet(key)

def encrypted_standard_query(record_id: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(f"ENCRYPTED_RECORD_{record_id}".encode())
        start = time.time()
        encrypted_data = s.recv(4096)
        end = time.time()

    decrypted_data = cipher.decrypt(encrypted_data)
    record = json.loads(decrypted_data.decode())
    print(f"[CLIENT - ENC STD] Received record: {record}")
    print(f"[CLIENT - ENC STD] Bandwidth: {len(encrypted_data)} bytes, Time: {round((end - start) * 1000, 2)} ms")

def encrypted_pir_query(record_id: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"ENCRYPTED_FULL_DB")
        start = time.time()
        encrypted_data = s.recv(65536)
        end = time.time()

    decrypted_data = cipher.decrypt(encrypted_data)
    records = json.loads(decrypted_data.decode())
    target = next((r for r in records if r["id"] == record_id), None)
    print(f"[CLIENT - ENC PIR] Desired record: {target}")
    print(f"[CLIENT - ENC PIR] Bandwidth: {len(encrypted_data)} bytes, Time: {round((end - start) * 1000, 2)} ms")

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Encrypted Standard Query (1 record)")
    print("2. Encrypted Trivial PIR (Full DB)")
    choice = input("Enter choice (1/2): ").strip()
    record_id = int(input("Enter record ID (1–50): ").strip())

    if choice == "1":
        encrypted_standard_query(record_id)
    elif choice == "2":
        encrypted_pir_query(record_id)
    else:
        print("Invalid choice.")
