import hashlib
import os
import base64

SALT_SIZE = 16  # Size of the salt in bytes
KEY_SIZE = 32  # Size of the key in bytes
iterations = 10000

def hash_password(password):
    """Hash a password with a given number of iterations"""
    salt = os.urandom(SALT_SIZE)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=KEY_SIZE
    )
    return f"{iterations}.{base64.b64encode(salt).decode('utf-8')}.{base64.b64encode(key).decode('utf-8')}"



def validate_password(stored_password, provided_password):
    """Validate a password"""
    try:
        iterations, salt, key = stored_password.split(".")
        salt = base64.b64decode(salt)
        key = base64.b64decode(key)
        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            provided_password.encode("utf-8"),
            salt,
            int(iterations),
            dklen=KEY_SIZE,
        )
        return new_key == key
    except ValueError as e:
        # Handle potential ValueError when splitting or decoding
        print(f"Error in validate_password: {e}")
        return False