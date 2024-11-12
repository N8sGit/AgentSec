# security/encryption_tools.py
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from security.permissions import get_clearance_level
from dotenv import load_dotenv
import os

load_dotenv()
salt_value = os.get('SALT_VALUE')

def generate_key(clearance_level: int, agent_name: str) -> bytes:
    """Generate a secure key based on clearance level and agent name."""
    password = f"{agent_name}_{clearance_level}".encode()
    salt = b'unique_salt_value'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def encrypt_data(data: str, clearance_level: int, agent_name: str) -> bytes:
    """Encrypt data using the generated key."""
    key = generate_key(clearance_level, agent_name)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data: bytes, agent_name: str) -> str:
    """Decrypt data using the agent's key."""
    agent_level = get_clearance_level(agent_name)
    key = generate_key(agent_level, agent_name)
    fernet = Fernet(key)
    try:
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return decrypted_data
    except Exception:
        return None  # Decryption failed due to insufficient clearance