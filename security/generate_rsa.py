# This is for demonstration purposes, in a real world application you'd want to do this more securely
import rsa

# Generate RSA key pair
(pubkey, privkey) = rsa.newkeys(2048)

# Save the public key to a file
with open("public_key.pem", "wb") as pub_file:
    pub_file.write(pubkey.save_pkcs1())

# Save the private key to a file
# Note, in production, you'd do this differently, for demonstration purposes only
with open("private_key.pem", "wb") as priv_file:
    priv_file.write(privkey.save_pkcs1())