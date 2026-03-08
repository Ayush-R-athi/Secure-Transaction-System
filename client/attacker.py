import requests
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

SERVER_URL = "http://127.0.0.1:8000"

def load_keys():
    with open("../keys/client_private.pem", "rb") as f:
        client_private = RSA.import_key(f.read())
    with open("../keys/server_public.pem", "rb") as f:
        server_public = RSA.import_key(f.read())
    return client_private, server_public

def intercept_and_build_envelope():
    """Simulates capturing a perfectly valid transaction envelope."""
    client_private_key, server_public_key = load_keys()
    server_nonce = requests.get(f"{SERVER_URL}/get-nonce").json()["nonce"]
    
    transaction_data = {"sender": "Ayush", "receiver": "Hacker", "amount": 999999, "currency": "INR", "purpose": "Theft"}
    payload_str = json.dumps(transaction_data)
    
    data_to_sign = (payload_str + server_nonce).encode('utf-8')
    h = SHA256.new(data_to_sign)
    signature = pss.new(client_private_key).sign(h)
    
    aes_session_key = get_random_bytes(32)
    cipher_aes = AES.new(aes_session_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(payload_str.encode('utf-8'))
    
    cipher_rsa = PKCS1_OAEP.new(server_public_key)
    wrapped_aes_key = cipher_rsa.encrypt(aes_session_key)
    
    return {
        "nonce": server_nonce,
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "aes_nonce": base64.b64encode(cipher_aes.nonce).decode('utf-8'),
        "auth_tag": base64.b64encode(tag).decode('utf-8'),
        "wrapped_key": base64.b64encode(wrapped_aes_key).decode('utf-8'),
        "signature": base64.b64encode(signature).decode('utf-8')
    }

print("\n" + "="*50)
print("💀 INITIATING HACKER SIMULATION MODULE 💀")
print("="*50)

# ---------------------------------------------------------
# ATTACK 1: REPLAY ATTACK (Double Spending)
# ---------------------------------------------------------
print("\n[+] Attacker intercepts a valid transaction envelope...")
valid_envelope = intercept_and_build_envelope()

print("[+] Sending the valid transaction normally (First Time)...")
requests.post(f"{SERVER_URL}/process-transaction", json=valid_envelope)

print("\n💥 ATTACK 1: Attempting Replay Attack (Sending exact same envelope again)")
response_replay = requests.post(f"{SERVER_URL}/process-transaction", json=valid_envelope)

print(f"SERVER RESPONSE [{response_replay.status_code}]:")
print(json.dumps(response_replay.json(), indent=4))


# ---------------------------------------------------------
# ATTACK 2: DATA TAMPERING (Man-in-the-Middle)
# ---------------------------------------------------------
print("\n" + "="*50)
print("💥 ATTACK 2: DATA TAMPERING (Modifying Ciphertext)")
print("="*50)
print("[+] Attacker intercepts a NEW transaction and alters the encrypted payload...")

tampered_envelope = intercept_and_build_envelope()

# We take the Base64 ciphertext, convert it to a list, change the 10th character, and join it back.
# This simulates an attacker flipping bits to try and change the money amount.
tampered_ciphertext = list(tampered_envelope["ciphertext"])
tampered_ciphertext[10] = 'X' if tampered_ciphertext[10] != 'X' else 'Y'
tampered_envelope["ciphertext"] = "".join(tampered_ciphertext)

print("[+] Ciphertext altered! Sending tampered envelope to server...")
response_tamper = requests.post(f"{SERVER_URL}/process-transaction", json=tampered_envelope)

print(f"SERVER RESPONSE [{response_tamper.status_code}]:")
print(json.dumps(response_tamper.json(), indent=4))
print("\nSimulation Complete. The server holds strong.")