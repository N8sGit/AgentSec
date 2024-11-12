# Note: Run this once in the terminal and paste the result 
import secrets
secret_key =  secrets.token_urlsafe(32)
print('secret key', secret_key)
salt_value =  secrets.token_urlsafe(32)
print('salt_value', salt_value)



