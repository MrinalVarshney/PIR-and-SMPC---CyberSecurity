import socket
import json
import time

HOST = '127.0.0.1'
PORT = 65432

def query_standard(record_id: int):
    """Query only one record (standard query)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(f"RECORD_{record_id}".encode())
        start = time.time()
        data = s.recv(4096)
        end = time.time()

    try:
        record = json.loads(data.decode())
        print(f"[CLIENT - STANDARD] Received: {record}")
    except:
        print(f"[CLIENT - STANDARD] Response: {data.decode()}")

    print(f"[CLIENT - STANDARD] Bandwidth used: {len(data)} bytes")
    print(f"[CLIENT - STANDARD] Query time: {round((end - start) * 1000, 2)} ms")


def query_trivial_pir(record_id: int):
    """Query all records (trivial PIR)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"FULL_DB")
        start = time.time()
        data = s.recv(65536)
        end = time.time()

    records = json.loads(data.decode())
    target_record = next((r for r in records if r["id"] == record_id), None)
    print(f"[CLIENT - TRIVIAL PIR] Desired record: {target_record}")
    print(f"[CLIENT - TRIVIAL PIR] Bandwidth used: {len(data)} bytes")
    print(f"[CLIENT - TRIVIAL PIR] Query time: {round((end - start) * 1000, 2)} ms")


if __name__ == "__main__":
    print("Choose query type:")
    print("1. Standard Query (fetch single record)")
    print("2. Trivial PIR (fetch full database)")

    choice = input("Enter choice (1/2): ").strip()
    record_id = int(input("Enter record ID (1–50): ").strip())

    if choice == "1":
        query_standard(record_id)
    elif choice == "2":
        query_trivial_pir(record_id)
    else:
        print("Invalid choice.")
