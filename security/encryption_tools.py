# security/encryption_tools.py
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from security.permissions import get_clearance_level
from dotenv import load_dotenv
import os

load_dotenv()
salt_value = os.getenv('SALT_VALUE')

def generate_key(clearance_level: int, agent_name: str) -> bytes:
    """Generate a secure key based on clearance level and agent name."""
    if isinstance(salt_value, str):
        salt = salt_value.encode('utf-8')  # Convert to bytes if not already
    else:
        salt = salt_value  # Assume salt_value is already bytes
    
    password = f"{agent_name}_{clearance_level}".encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_data(data: str, clearance_level: int, agent_name: str) -> str:
    """Encrypt data using the generated key and return a base64-encoded string."""
    key = generate_key(clearance_level, agent_name)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    # Convert bytes to a base64 string
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data: str, agent_name: str) -> str:
    """Decrypt a base64-encoded string using the agent's key."""
    print("[DEBUG] Starting decryption process.")
    
    # Retrieve the agent's clearance level
    try:
        agent_level = get_clearance_level(agent_name)
        print(f"[DEBUG] Retrieved clearance level: {agent_level} for agent: {agent_name}")
    except Exception as e:
        print(f"[ERROR] Failed to retrieve clearance level for agent {agent_name}: {e}")
        return None
    
    # Generate the decryption key
    try:
        key = generate_key(agent_level, agent_name)
        print(f"[DEBUG] Generated decryption key: {key}")
    except Exception as e:
        print(f"[ERROR] Failed to generate decryption key for agent {agent_name}: {e}")
        return None

    # Initialize Fernet with the generated key
    try:
        fernet = Fernet(key)
        print(f"[DEBUG] Fernet object successfully initialized.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Fernet: {e}")
        return None
    
    # Attempt to decode the base64-encoded string
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        print(f"[DEBUG] Base64-decoded encrypted data: {encrypted_bytes}")
    except Exception as e:
        print(f"[ERROR] Failed to decode base64 data: {e}")
        return None

    # Attempt to decrypt the data
    try:
        decrypted_data = fernet.decrypt(encrypted_bytes).decode()
        print(f"[DEBUG] Successfully decrypted data: {decrypted_data}")
        return decrypted_data
    except Exception as e:
        print(f"[ERROR] Error decrypting data: {e}")
        return None