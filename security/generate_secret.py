# Note: Run this once in the terminal via python -m  security.generate_secret and paste the result in .env
import secrets
secret_key =  secrets.token_urlsafe(32)
print('secret key', secret_key)
salt_value =  secrets.token_urlsafe(32)
print('salt_value', salt_value)



