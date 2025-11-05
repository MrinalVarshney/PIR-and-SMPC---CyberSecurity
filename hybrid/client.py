# hybrid_client.py
import socket
import json
import time
from cryptography.hazmat.primitives.asymmetric import padding, serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

HOST = "127.0.0.1"
PORT = 65434

def recv_all(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # Step A: receive RSA public key PEM
    pub_len_bytes = recv_all(s, 4)
    pub_len = int.from_bytes(pub_len_bytes, "big")
    pem_pub = recv_all(s, pub_len)
    server_pub = serialization.load_pem_public_key(pem_pub)
    print("[CLIENT] Received server RSA public key.")

    # Step B: generate AES key and encrypt it with RSA public key
    aes_key = AESGCM.generate_key(bit_length=256)  # 32 bytes
    encrypted_aes_key = server_pub.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )
    # send length + encrypted key
    s.sendall(len(encrypted_aes_key).to_bytes(2, "big") + encrypted_aes_key)
    print("[CLIENT] Sent AES key encrypted with server RSA public key.")

    # helper to send AES-encrypted message and receive AES-encrypted response
    def send_aes_request_and_recv_reply(request_str: str):
        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, request_str.encode(), None)
        s.sendall(len(nonce).to_bytes(2, "big") + nonce + ct)
        # receive reply header: first 2 bytes len(nonce)
        hdr = s.recv(2)
        if not hdr:
            return None
        nonce_len = int.from_bytes(hdr, "big")
        nonce = s.recv(nonce_len)
        ct = s.recv(65536)
        # decrypt
        return aesgcm.decrypt(nonce, ct, None)

    # Demo: Standard vs Trivial PIR
    # Standard
    rr = send_aes_request_and_recv_reply("RECORD_25")
    print("[CLIENT] Standard (encrypted) response:", json.loads(rr.decode()))

    # Trivial PIR (encrypted full DB)
    rr2 = send_aes_request_and_recv_reply("FULL_DB")
    records = json.loads(rr2.decode())
    target = next((r for r in records if r["id"] == 25), None)
    print("[CLIENT] Trivial PIR (encrypted) desired record:", target)
