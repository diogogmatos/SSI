from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


def cipher(clean_data: bytes, key: bytes) -> bytes:
    """
    Cifra texto usando AES CTR.
    """

    if not isinstance(clean_data, bytes):
        raise ValueError("clean_data must be bytes")

    # Gerar nonce
    nonce = os.urandom(16)

    # Cifrar
    cipher = Cipher(algorithms.AES(key), mode=modes.CTR(nonce))
    encryptor = cipher.encryptor()
    ciphered_data = encryptor.update(clean_data) + encryptor.finalize()

    return nonce + ciphered_data


def decipher(data: bytes, key: bytes) -> bytes:
    """
    Decifra um ficheiro usando AES CTR.
    """

    if not isinstance(data, bytes):
        raise ValueError("data must be bytes")

    # Separar nonce do criptograma
    nonce = data[:16]
    ciphered_data = data[16:]

    # Decifrar
    cipher = Cipher(algorithms.AES(key), mode=modes.CTR(nonce))
    decryptor = cipher.decryptor()
    clean_data = decryptor.update(ciphered_data) + decryptor.finalize()

    return clean_data
