import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

salt_file = "salt.bin"
k_file = "key.key"

def get_salt():
    try:
        with open(salt_file, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        # Create salt if it doesn't exist
        salt = os.urandom(16)
        with open(salt_file, 'wb') as f:
            f.write(salt)
        print(f"Salt created and saved to {salt_file}")
        return salt

def create_key(master_pwd):
    # key = Fernet.generate_key() # generate a key and save it into a file
    salt = get_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_pwd.encode()))
    return key

def write_key(key):
    with open(k_file, "wb") as key_file: 
        key_file.write(key)

# # One-Time Key Creation
# master_pwd = input("Set master password: ")
# key = create_key(master_pwd)
# write_key(key)
# print("key created successfully, you can now comment out this part")