# hybrid_server.py
import socket
import json
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Dummy DB
database = [{"id": i, "data": f"Record_{i}_data"} for i in range(1, 51)]

HOST = "127.0.0.1"
PORT = 65434

# 1) Generate RSA keypair (server side)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
pem_pub = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print("[SERVER] RSA public key (PEM) -- share this with clients automatically on connect.")
# We will send pem_pub over socket to client (it's okay to be public)

def decrypt_aes_key(encrypted_key: bytes) -> bytes:
    # RSA decrypt AES key received from client
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )
    return aes_key

def encrypt_and_send_aes_payload(conn, aes_key: bytes, plaintext_bytes: bytes):
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
    ct = aesgcm.encrypt(nonce, plaintext_bytes, None)
    # send nonce length + nonce + ciphertext
    payload = len(nonce).to_bytes(2, "big") + nonce + ct
    conn.sendall(payload)
    return len(payload)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\n[SERVER] Connected by {addr}")
            # Step A: send RSA public key PEM (plain)
            conn.sendall(len(pem_pub).to_bytes(4, "big") + pem_pub)
            # Step B: receive encrypted AES key length + encrypted key
            enc_len_bytes = conn.recv(2)
            if len(enc_len_bytes) < 2:
                print("[SERVER] No AES key sent; closing.")
                continue
            enc_len = int.from_bytes(enc_len_bytes, "big")
            encrypted_aes_key = conn.recv(enc_len)
            aes_key = decrypt_aes_key(encrypted_aes_key)
            print(f"[SERVER] Received encrypted AES key ({enc_len} bytes). Decrypted AES key length: {len(aes_key)} bytes")

            # Now handle client requests over the AES channel
            # Client will send AES-encrypted requests as: [nonce_len(2)][nonce][ciphertext]
            while True:
                hdr = conn.recv(2)
                if not hdr:
                    break
                nonce_len = int.from_bytes(hdr, "big")
                nonce = conn.recv(nonce_len)
                # read remaining packet (we'll read with a timeout loop for simplicity)
                # For demo, assume a single recv returns the ciphertext
                ct = conn.recv(65536)
                if not ct:
                    break

                aesgcm = AESGCM(aes_key)
                try:
                    request_bytes = aesgcm.decrypt(nonce, ct, None)
                except Exception as e:
                    print("[SERVER] Decrypt error:", e)
                    break

                request = request_bytes.decode()
                print(f"[SERVER] (AES) Client request: {request}")

                if request.startswith("RECORD_"):
                    record_id = int(request.split("_")[1])
                    record = next((r for r in database if r["id"] == record_id), None)
                    if record:
                        payload = json.dumps(record).encode()
                    else:
                        payload = b"Record not found"

                elif request == "FULL_DB":
                    payload = json.dumps(database).encode()

                else:
                    payload = b"Invalid request"

                start = time.time()
                size = encrypt_and_send_aes_payload(conn, aes_key, payload)
                end = time.time()
                print(f"[SERVER] Sent AES-encrypted reply of {size} bytes in {round((end-start)*1000,2)} ms")
