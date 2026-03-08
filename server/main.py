from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import uuid
import json
import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

app = FastAPI(title="Secure Transaction Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your local HTML file to talk to the server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
except redis.ConnectionError:
    print("❌ Critical Error: Could not connect to Redis.")

# --- Pydantic Models for incoming JSON ---
class DigitalEnvelope(BaseModel):
    nonce: str
    ciphertext: str
    aes_nonce: str
    auth_tag: str
    wrapped_key: str
    signature: str

class TransactionInput(BaseModel):
    sender: str
    receiver: str
    amount: float
    currency: str = "INR"
    purpose: str

# --- Load Keys ---
# Note: Since uvicorn runs from the root directory, we use "keys/" path
try:
    with open("keys/server_private.pem", "rb") as f:
        SERVER_PRIVATE_KEY = RSA.import_key(f.read())
    with open("keys/client_public.pem", "rb") as f:
        CLIENT_PUBLIC_KEY = RSA.import_key(f.read())
except Exception as e:
    print(f"Key loading error. Ensure you run uvicorn from the root folder. Error: {e}")

# ==========================================
# ADDED: Health Check Endpoint for Dashboard
# ==========================================
@app.get("/")
def health_check():
    """Allows the UI Dashboard to ping the server and verify it is online."""
    return {"status": "Secure Server is running."}


@app.get("/get-nonce")
def generate_nonce():
    new_nonce = str(uuid.uuid4())
    redis_client.setex(name=new_nonce, time=60, value="valid")
    return {"nonce": new_nonce, "expires_in": 60}


@app.post("/process-transaction")
def process_transaction(envelope: DigitalEnvelope):
    print("\n--- NEW ENVELOPE RECEIVED ---")
    
    # 1. ANTI-REPLAY CHECK (Check Nonce first to save computation time)
    if not redis_client.exists(envelope.nonce):
        print("🚨 REPLAY ATTACK DETECTED: Invalid or expired nonce.")
        raise HTTPException(status_code=403, detail="Replay Attack Detected. Nonce invalid.")
    
    # Burn the nonce immediately so it can never be used again
    redis_client.delete(envelope.nonce)
    print("✅ Nonce verified and burned.")

    try:
        # Decode the Base64 strings back into raw bytes
        wrapped_key = base64.b64decode(envelope.wrapped_key)
        ciphertext = base64.b64decode(envelope.ciphertext)
        aes_nonce = base64.b64decode(envelope.aes_nonce)
        auth_tag = base64.b64decode(envelope.auth_tag)
        signature = base64.b64decode(envelope.signature)

        # 2. UNWRAP THE SESSION KEY
        cipher_rsa = PKCS1_OAEP.new(SERVER_PRIVATE_KEY)
        aes_session_key = cipher_rsa.decrypt(wrapped_key)
        print("✅ AES Session Key successfully unwrapped.")

        # 3. DECRYPT THE PAYLOAD
        cipher_aes = AES.new(aes_session_key, AES.MODE_GCM, nonce=aes_nonce)
        decrypted_payload = cipher_aes.decrypt_and_verify(ciphertext, auth_tag)
        payload_str = decrypted_payload.decode('utf-8')
        print("✅ Payload decrypted and GCM authentication tag verified.")

        # 4. VERIFY THE DIGITAL SIGNATURE
        data_to_verify = (payload_str + envelope.nonce).encode('utf-8')
        h = SHA256.new(data_to_verify)
        
        # If this fails, it throws a ValueError automatically
        pss.new(CLIENT_PUBLIC_KEY).verify(h, signature)
        print("✅ Identity mathematically proven. Signature is valid.")

        # 5. PROCESS THE TRANSACTION
        transaction_data = json.loads(payload_str)
        print(f"💰 TRANSACTION APPROVED: {transaction_data['amount']} {transaction_data['currency']} to {transaction_data['receiver']}")
        
        return {
            "status": "success",
            "message": "Transaction verified and approved via Zero-Trust protocol.",
            "data": transaction_data
        }

    except ValueError as e:
        print("🚨 TAMPERING DETECTED: Signature or Authentication Tag mismatch.")
        raise HTTPException(status_code=400, detail="Data Integrity Compromised.")
    except Exception as e:
        print(f"🚨 UNEXPECTED ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")


@app.post("/build-custom-envelope")
def build_custom_envelope(tx_data: TransactionInput):
    """Takes user input from the UI and builds a real cryptographic envelope."""
    try:
        with open("keys/client_private.pem", "rb") as f:
            client_private_key = RSA.import_key(f.read())
        with open("keys/server_public.pem", "rb") as f:
            server_public_key = RSA.import_key(f.read())
            
        # 1. Get a real nonce
        server_nonce = str(uuid.uuid4())
        redis_client.setex(name=server_nonce, time=60, value="valid")
        
        # 2. Use the custom data from the web form
        payload_str = json.dumps(tx_data.model_dump())
        
        # 3. Hash and Sign
        data_to_sign = (payload_str + server_nonce).encode('utf-8')
        h = SHA256.new(data_to_sign)
        signature = pss.new(client_private_key).sign(h)
        
        # 4. Encrypt (AES)
        aes_session_key = get_random_bytes(32)
        cipher_aes = AES.new(aes_session_key, AES.MODE_GCM)
        ciphertext, tag = cipher_aes.encrypt_and_digest(payload_str.encode('utf-8'))
        
        # 5. Wrap (RSA)
        cipher_rsa = PKCS1_OAEP.new(server_public_key)
        wrapped_aes_key = cipher_rsa.encrypt(aes_session_key)
        
        # 6. Return the perfectly valid dynamic envelope
        return {
            "nonce": server_nonce,
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "aes_nonce": base64.b64encode(cipher_aes.nonce).decode('utf-8'),
            "auth_tag": base64.b64encode(tag).decode('utf-8'),
            "wrapped_key": base64.b64encode(wrapped_aes_key).decode('utf-8'),
            "signature": base64.b64encode(signature).decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))