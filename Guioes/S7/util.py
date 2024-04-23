import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

master_key = "supersecretkey"


def decrypt_AESGCM(nonce, salt, content):
    key = generate_master_key(salt)
    aesgcm = AESGCM(key)
    ct = aesgcm.decrypt(nonce, content, None)
    return ct


def encrypt_AESGCM(content):
    nonce = os.urandom(12)
    salt = os.urandom(16)

    key = generate_master_key(salt)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, content, None)

    return nonce + salt + encrypted


def generate_master_key(salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = kdf.derive(master_key.encode())
    return key
