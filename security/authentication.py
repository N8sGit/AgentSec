import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key'

def generate_token(user_id, clearance_level):
    payload = {
        'user_id': user_id,
        'clearance_level': clearance_level,
        'exp': datetime.now() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def authenticate_source(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        print("Token expired.")
        return False
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return False