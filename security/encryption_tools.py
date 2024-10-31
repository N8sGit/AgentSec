from cryptography.fernet import Fernet
import base64
import hashlib
from permissions import get_clearance_level

# Generate a key based on clearance level
def generate_key(clearance_level):
    # Securely derive a key from the clearance level
    key_material = f"secret_key_material_{clearance_level}".encode()
    key = hashlib.sha256(key_material).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_data(data, clearance_level):
    key = generate_key(clearance_level)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data, agent_name):
    agent_level = get_clearance_level(agent_name)
    key = generate_key(agent_level)
    fernet = Fernet(key)
    try:
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return decrypted_data
    except Exception:
        return None  # Decryption failed due to insufficient clearance