import rsa
import hashlib
import time
import os

# Path constants for the keys (note: made explicit for proof of concept)
BASE_DIR = os.path.dirname(__file__)
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "keys", "public_key.pem")
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "keys", "private_key.pem")

def load_public_key():
    """Load the public key from a file."""
    with open(PUBLIC_KEY_PATH, "rb") as pub_file:
        return rsa.PublicKey.load_pkcs1(pub_file.read())

def load_private_key():
    """Load the private key from a file."""
    with open(PRIVATE_KEY_PATH, "rb") as priv_file:
        return rsa.PrivateKey.load_pkcs1(priv_file.read())

def sign_message(message: str) -> dict:
    """Sign a message with the private key."""
    privkey = load_private_key()  # Load private key for signing
    timestamp = int(time.time())
    message_data = f"{message}|{timestamp}"
    message_hash = hashlib.sha256(message_data.encode()).digest()

    # Sign the hash with the private key
    signature = rsa.sign(message_hash, privkey, 'SHA-256')

    return {
        "message": message,
        "timestamp": timestamp,
        "signature": signature
    }

def verify_signature(received_data: dict) -> bool:
    """Verify the signature of a message with the public key."""
    pubkey = load_public_key()  # Load public key for verification
    message = received_data["message"]
    timestamp = received_data["timestamp"]
    signature = received_data["signature"]

    # Verify timestamp (e.g., within 5 minutes)
    if abs(int(time.time()) - timestamp) > 300:  # 5 minutes
        print("Message expired.")
        return False

    # Recreate the hash
    message_data = f"{message}|{timestamp}"
    message_hash = hashlib.sha256(message_data.encode()).digest()

    # Verify the signature with the public key
    try:
        rsa.verify(message_hash, signature, pubkey)
        return True
    except rsa.VerificationError:
        print("Signature verification failed.")
        return False