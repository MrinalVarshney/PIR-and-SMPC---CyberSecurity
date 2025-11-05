import socket
import json
import time

# Create dummy database with 50 records
database = [{"id": i, "data": f"Record_{i}_data"} for i in range(1, 51)]

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("[SERVER] Waiting for connection...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\n[SERVER] Connected by {addr}")
            request = conn.recv(1024).decode()

            if request.startswith("RECORD_"):
                # ---------- Standard Query ----------
                record_id = int(request.split("_")[1])
                record = next((r for r in database if r["id"] == record_id), None)
                if record:
                    print(f"[SERVER] Standard query for record {record_id}")
                    start = time.time()
                    data = json.dumps(record).encode()
                    conn.sendall(data)
                    end = time.time()
                    print(f"[SERVER] Sent {len(data)} bytes in {round((end - start) * 1000, 2)} ms")
                else:
                    conn.sendall(b"Record not found")

            elif request == "FULL_DB":
                # ---------- Trivial PIR ----------
                print("[SERVER] Log: full database requested")
                start = time.time()
                data = json.dumps(database).encode()
                conn.sendall(data)
                end = time.time()
                print(f"[SERVER] Sent {len(data)} bytes in {round((end - start) * 1000, 2)} ms")

            else:
                print("[SERVER] Invalid request")
                conn.sendall(b"Invalid request")
