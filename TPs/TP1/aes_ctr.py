from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


def cipher_text(clean_text: str, key: bytes) -> bytes:
    """
    Cifra texto usando AES CTR.
    """

    # Gerar nonce
    nonce = os.urandom(16)

    # Cifrar
    cipher = Cipher(algorithms.AES(key), mode=modes.CTR(nonce))
    encryptor = cipher.encryptor()
    ciphered_text = encryptor.update(clean_text) + encryptor.finalize()

    return nonce + ciphered_text


def decipher_text(data: bytes, key: bytes) -> str:
    """
    Decifra um ficheiro usando AES CTR.
    """

    # Separar nonce do criptograma
    nonce = data[:16]
    ciphered_text = data[16:]

    # Decifrar
    cipher = Cipher(algorithms.AES(key), mode=modes.CTR(nonce))
    decryptor = cipher.decryptor()
    clean_text = decryptor.update(ciphered_text) + decryptor.finalize()

    return clean_text
