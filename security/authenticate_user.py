# authorize_user.py
import getpass
import hashlib
import jwt
from datetime import datetime, timedelta
import os 
from dotenv import load_dotenv
load_dotenv()

# Mock database: Define user credentials and clearance level for Nathan
AUTHORIZED_USERS = {
    "n": {
        "password_hash": hashlib.sha256("p".encode()).hexdigest(),
        "clearance_level": 3
    }
}

SECRET_KEY = os.getenv('SECRET_KEY')

def authenticate_user():
    """Authenticate the user through the terminal and return their clearance level if authorized."""
    # username = input("Enter your username: ")
    # password = getpass.getpass("Enter your password: ")
    username='n'
    password = 'p'
    user = AUTHORIZED_USERS.get(username)
    if user and hashlib.sha256(password.encode()).hexdigest() == user["password_hash"]:
        print("Authentication successful.")
        return user["clearance_level"]
    else:
        print("Authentication failed.")
        return None

def generate_token(clearance_level):
    """Generate a JWT token containing the user's clearance level."""
    payload = {
        "clearance_level": clearance_level,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Main entry point
if __name__ == "__main__":
    clearance_level = authenticate_user()
    if clearance_level is not None:
        user_token = generate_token(clearance_level)
        print(f"User authenticated with clearance level {clearance_level}.")
        print(f"Generated token: {user_token}")
    else:
        print("Authentication failed. Exiting.")