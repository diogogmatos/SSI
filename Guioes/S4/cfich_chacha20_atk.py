import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hmac
import os

def modify_ciphertext(file_name, position, plaintext_at_pos, new_plaintext_at_pos):
    with open(file_name, 'rb') as f:
        ciphertext = f.read()

    # Extract salt and nonce from the ciphertext
    salt = ciphertext[:16]
    nonce = ciphertext[16:32]
    ciphertext_data = ciphertext[32:]

    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(b"password")

    # Decrypt the ciphertext to obtain the original plaintext
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_plaintext = decryptor.update(ciphertext_data) + decryptor.finalize()

    # Modify the plaintext at the specified position
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(decrypted_plaintext) + padder.finalize()
    modified_padded_plaintext = padded_plaintext[:position] + new_plaintext_at_pos.encode() + padded_plaintext[position+len(new_plaintext_at_pos):]

    # Re-encrypt the modified plaintext
    unpadder = padding.PKCS7(128).unpadder()
    modified_plaintext = unpadder.update(modified_padded_plaintext) + unpadder.finalize()
    encryptor = cipher.encryptor()
    modified_ciphertext = encryptor.update(modified_plaintext) + encryptor.finalize()

    # Write the modified ciphertext to the file
    with open(file_name + '.attck', 'wb') as f:
        f.write(salt + nonce + modified_ciphertext)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python chacha20_int_attck.py <fctxt> <pos> <ptxtAtPos> <newPtxtAtPos>")
        sys.exit(1)

    file_name = sys.argv[1]
    position = int(sys.argv[2])
    plaintext_at_pos = sys.argv[3]
    new_plaintext_at_pos = sys.argv[4]

    modify_ciphertext(file_name, position, plaintext_at_pos, new_plaintext_at_pos)
    print("Ciphertext modified successfully.")
