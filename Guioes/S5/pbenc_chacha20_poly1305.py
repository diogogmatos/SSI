import os
import sys

from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def decrypt(salt, nonce, signature, content, password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    key = kdf.derive(password.encode())
    cipher = Cipher(algorithms.AES(key[:32]), modes.CTR(nonce))
    decryptor = cipher.decryptor()

    original_content = decryptor.update(content)

    h = hmac.HMAC(key[32:], hashes.SHA256())
    h.update(content)
    h.verify(signature)

    return original_content


def encrypt(content, password):
    salt = os.urandom(16)
    nonce = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )

    key = kdf.derive(password.encode())
    chacha = ChaCha20Poly1305(key)
    encrypted = chacha.encrypt(nonce, content, None)

    return salt, nonce, encrypted


def setup_key():
    return os.urandom(32)


def main(args):
    if len(args) < 2:
        print("Usage:"
              "\n\tpython3 pbenc_chacha20.py enc <fich>"
              "\n\tpython3 pbenc_chacha20.py dec <fich>")
        return

    filename = args[1]

    password = input()

    if args[0] == 'enc':
        with open(filename, 'rb') as file_to_encrypt:
            content = file_to_encrypt.read()
            salt, nonce, signature, cipher_text = encrypt(content, password)
        with open(filename + '.enc', 'wb') as output_file:
            output_file.write(salt)
            output_file.write(nonce)
            output_file.write(signature)
            output_file.write(cipher_text)
    if args[0] == 'dec':
        with open(filename, 'rb') as file_to_decrypt:
            salt = file_to_decrypt.read(16)
            nonce = file_to_decrypt.read(16)
            signature = file_to_decrypt.read(32)
            content = file_to_decrypt.read()
        with open(filename + '.dec', 'wb') as output_file:
            output_file.write(decrypt(salt, nonce, signature, content, password))


if __name__ == '__main__':
    main(sys.argv[1:])

