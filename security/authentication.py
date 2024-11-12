# security/authentication.py
import jwt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

# Secure the secret key
load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')

def generate_token(user_id: str, clearance_level: int) -> str:
    """Generate a JWT token for authentication."""
    payload = {
        'user_id': user_id,
        'clearance_level': clearance_level,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def authenticate_source(token: str) -> bool:
    """Authenticate the source using the provided token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        print("Token expired.")
        return False
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return False