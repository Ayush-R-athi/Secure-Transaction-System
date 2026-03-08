import requests
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

# --- Configuration ---
SERVER_URL = "http://127.0.0.1:8000"

def load_keys():
    """Loads the Client's Private Key (to sign) and Server's Public Key (to wrap)."""
    with open("../keys/client_private.pem", "rb") as f:
        client_private_key = RSA.import_key(f.read())
        
    with open("../keys/server_public.pem", "rb") as f:
        server_public_key = RSA.import_key(f.read())
        
    return client_private_key, server_public_key

def build_digital_envelope():
    client_private_key, server_public_key = load_keys()

    print("1. Initiating Secure Handshake...")
    # Fetch the Anti-Replay Nonce from the server
    response = requests.get(f"{SERVER_URL}/get-nonce")
    server_nonce = response.json()["nonce"]
    print(f"   [+] Received Nonce: {server_nonce}")

    # The Transaction Data
    transaction_data = {
        "sender": "Ayush",
        "receiver": "VIT University",
        "amount": 50000,
        "currency": "INR",
        "purpose": "Tuition Fee"
    }
    
    # Convert data to a JSON string so we can hash and encrypt it
    payload_str = json.dumps(transaction_data)
    
    print("\n2. Generating Digital Signature (RSA-PSS)...")
    # To prevent tampering, we hash the Data + Nonce together
    data_to_sign = (payload_str + server_nonce).encode('utf-8')
    h = SHA256.new(data_to_sign)
    
    # Sign the hash using the Client's Private Key
    signature = pss.new(client_private_key).sign(h)
    print("   [+] Payload hashed and signed.")

    print("\n3. Encrypting Payload (AES-256 GCM)...")
    # Generate a random 256-bit (32-byte) session key for high-speed encryption
    aes_session_key = get_random_bytes(32)
    
    # Encrypt the transaction data
    cipher_aes = AES.new(aes_session_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(payload_str.encode('utf-8'))
    print("   [+] Data encrypted securely.")

    print("\n4. Wrapping the AES Key (RSA-OAEP)...")
    # Encrypt the AES session key using the Server's Public Key
    cipher_rsa = PKCS1_OAEP.new(server_public_key)
    wrapped_aes_key = cipher_rsa.encrypt(aes_session_key)
    print("   [+] Session key wrapped.")

    print("\n5. Assembling the Digital Envelope...")
    # We must encode raw bytes into Base64 so they can be transmitted over HTTP as JSON
    digital_envelope = {
        "nonce": server_nonce,
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "aes_nonce": base64.b64encode(cipher_aes.nonce).decode('utf-8'), # AES requires its own initialization vector
        "auth_tag": base64.b64encode(tag).decode('utf-8'),               # The GCM tamper-evident seal
        "wrapped_key": base64.b64encode(wrapped_aes_key).decode('utf-8'),
        "signature": base64.b64encode(signature).decode('utf-8')
    }

    print("\n================ DIGITAL ENVELOPE ================")
    print(json.dumps(digital_envelope, indent=4))
    print("==================================================")
    
    print("==================================================")
    
    print("\n6. Transmitting to Secure Server...")
    response = requests.post(f"{SERVER_URL}/process-transaction", json=digital_envelope)
    
    print(f"\nSERVER RESPONSE [{response.status_code}]:")
    print(json.dumps(response.json(), indent=4))
    
    return digital_envelope

if __name__ == "__main__":
    build_digital_envelope()