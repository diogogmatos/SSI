from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import os
import sys

def cifrar_ficheiro(fich, password, fsaida):
    """
    Cifra um ficheiro usando ChaCha20.
    """
    with open(fich, "rb") as f:
        texto_limpo = f.read()

    # Gerar salt
    salt = os.urandom(16)

    # Gerar chave da password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    chave = kdf.derive(password.encode('utf-8'))

    # Gerar nonce
    nonce = os.urandom(16)

    # Cifrar
    cifra = Cipher(algorithms.ChaCha20(chave, nonce), mode=None)
    encryptor = cifra.encryptor()
    texto_encriptado = encryptor.update(texto_limpo) + encryptor.finalize()

    # Guardar ficheiro cifrado
    with open(fsaida, "wb") as f:
        f.write(nonce + salt + texto_encriptado)

def decifrar_ficheiro(fich, password, fsaida):
    """
    Decifra um ficheiro usando ChaCha20.
    """
    with open(fich, "rb") as f:
        data = f.read()

    # Separar nonce e salt do criptograma
    nonce = data[:16]
    salt = data[16:32]
    texto_encriptado = data[32:]

    # Verificar password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    chave = kdf.derive(password.encode("utf-8"))

    # Decifrar
    cifra = Cipher(algorithms.ChaCha20(chave, nonce), mode=None)
    decryptor = cifra.decryptor()
    texto_limpo = decryptor.update(texto_encriptado) + decryptor.finalize()

    # Guardar ficheiro decifrado
    with open(fsaida, "wb") as f:
        f.write(texto_limpo)


def main(argv: list[str]):
    # Ler argumentos
    operacao = argv[1]

    if operacao == "enc":
        if not argv[2]:
            print("Erro: ficheiro de texto-limpo não especificado")
            return
        fich = argv[2]
        password = input("Por favor, insira e password: ")
        fsaida = fich + ".enc"
        cifrar_ficheiro(fich, password, fsaida)
        print("Ficheiro cifrado em", fsaida)

    elif operacao == "dec":
        if not argv[2]:
            print("Erro: ficheiro cifrado não especificado")
            return
        fich = argv[2]
        password = input("Por favor, insira e password: ")
        fsaida = fich.split(".")[0] + ".txt.dec"
        decifrar_ficheiro(fich, password, fsaida)
        print("Ficheiro decifrado em", fsaida)

    else:
        print("Erro: operação inválida")


if __name__ == "__main__":
    main(sys.argv)
