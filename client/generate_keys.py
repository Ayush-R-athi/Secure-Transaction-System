from Crypto.PublicKey import RSA
import os

def generate_key_pair(entity_name):
    print(f"Generating RSA-4096 key pair for {entity_name}...")
    
    # Generate a 4096-bit RSA key
    key = RSA.generate(4096)
    
    # Extract the private and public keys
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    
    # Save the Private Key (Keep this secret!)
    with open(f"../keys/{entity_name}_private.pem", "wb") as priv_file:
        priv_file.write(private_key)
        
    # Save the Public Key (Share this with the world)
    with open(f"../keys/{entity_name}_public.pem", "wb") as pub_file:
        pub_file.write(public_key)
        
    print(f"Success! Keys saved in the /keys folder for {entity_name}.\n")

if __name__ == "__main__":
    # Ensure the keys directory exists
    os.makedirs("../keys", exist_ok=True)
    
    # Generate keys for the Client (Sender)
    generate_key_pair("client")
    
    # Generate keys for the Server (Bank)
    generate_key_pair("server")