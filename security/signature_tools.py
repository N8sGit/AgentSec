import rsa
import hashlib
import time
import os
from messages.messages import InstructionMessage
from utils.serializers import deserialize_message, serialize_message

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

def sign_message(data: InstructionMessage) -> InstructionMessage:
    """
    Sign a message with the private key and return the signed and timestamped InstructionMessage.
    """
    privkey = load_private_key()
    timestamp = int(time.time())  # Add current timestamp
    
    # Serialize the message to prepare for signing
    message_dict = serialize_message(data)
    message_str = f"{message_dict['message']}|{message_dict['sender']}|{message_dict['token']}|{timestamp}"
    message_hash = hashlib.sha256(message_str.encode()).digest()

    # Generate signature and encode it as a string
    signature = rsa.sign(message_hash, privkey, 'SHA-256')
    message_dict['signature'] = signature.hex()
    message_dict['timestamp'] = timestamp

    # Return a Pydantic model from the updated dictionary
    return deserialize_message(message_dict, InstructionMessage)

def verify_signature(received_data: InstructionMessage) -> bool:
    """Verify the signature of a message with the public key."""
    try:
        # Convert InstructionMessage to a dictionary for processing
        message_dict = serialize_message(received_data)
        pubkey = load_public_key()  # Load public key for verification
        
        # Extract fields
        message = message_dict["message"]
        sender = message_dict["sender"]
        token = message_dict["token"]
        timestamp = message_dict["timestamp"]
        signature = message_dict["signature"]

        print(f"Debug: Loaded public key: {pubkey}")
        print(f"Debug: Extracted data - message: {message}, sender: {sender}, token: {token}, timestamp: {timestamp}, signature: {signature}")

        # Convert the signature from hex string to bytes
        signature_bytes = bytes.fromhex(signature)
        print(f"Debug: Converted signature to bytes: {signature_bytes}")

        # Verify timestamp (e.g., within 5 minutes)
        current_time = int(time.time())
        print(f"Debug: Current time: {current_time}, Message timestamp: {timestamp}, Time difference: {abs(current_time - timestamp)}")

        if abs(current_time - timestamp) > 300:  # 5 minutes
            print("Debug: Message expired.")
            return False

        # Recreate the hash
        message_data = f"{message}|{sender}|{token}|{timestamp}"
        message_hash = hashlib.sha256(message_data.encode()).digest()
        print(f"Debug: Recreated message hash: {message_hash}")

        # Verify the signature with the public key
        try:
            rsa.verify(message_hash, signature_bytes, pubkey)
            print("Debug: Signature verification successful.")
            return True
        except rsa.VerificationError:
            print("Debug: Signature verification failed.")
            return False

    except KeyError as e:
        print(f"Debug: Missing key in received data: {e}")
        return False
    except Exception as e:
        print(f"Debug: An unexpected error occurred during verification: {e}")
        return False