from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

import os
import sys

def gerar_chave(fkey):
    """
    Gera uma chave e guarda-a em ficheiro.
    """
    chave = os.urandom(32)
    with open(fkey, "wb") as f:
        f.write(chave)

def cifrar_ficheiro(fich, fkey, fsaida):
    """
    Cifra um ficheiro usando AES CBC.
    """
    with open(fich, "rb") as f:
        texto_limpo = f.read()

    # Ler chave do ficheiro
    with open(fkey, "rb") as f:
        chave = f.read()

    # Gerar nonce
    nonce = os.urandom(16)

    # Cifrar
    cifra = Cipher(algorithms.AES(chave), mode=modes.CBC(nonce))
    encryptor = cifra.encryptor()
    padder = PKCS7(128).padder()
    texto_padded = padder.update(texto_limpo) + padder.finalize()
    texto_encriptado = encryptor.update(texto_padded) + encryptor.finalize()

    # Guardar ficheiro cifrado
    with open(fsaida, "wb") as f:
        f.write(nonce + texto_encriptado)

def decifrar_ficheiro(fich, fkey, fsaida):
    """
    Decifra um ficheiro usando AES CBC.
    """
    with open(fich, "rb") as f:
        data = f.read()

    # Separar nonce do criptograma
    nonce = data[:16]
    texto_encriptado = data[16:]

    # Ler chave do ficheiro
    with open(fkey, "rb") as f:
        chave = f.read()

    # Decifrar
    cifra = Cipher(algorithms.AES(chave), mode=modes.CBC(nonce))
    decryptor = cifra.decryptor()
    texto_padded = decryptor.update(texto_encriptado) + decryptor.finalize()
    unpadder = PKCS7(128).unpadder()
    texto_limpo = unpadder.update(texto_padded) + unpadder.finalize()

    # Guardar ficheiro decifrado
    with open(fsaida, "wb") as f:
        f.write(texto_limpo)


def main(argv: list[str]):
    # Ler argumentos
    operacao = argv[1]

    if operacao == "setup":
        if not argv[2]:
            print("Erro: ficheiro de chave não especificado")
            return
        fkey = argv[2]
        gerar_chave(fkey)
        print("Chave gerada em", fkey)

    elif operacao == "enc":
        if not argv[2] or not argv[3]:
            print("Erro: ficheiro de texto-limpo e chave não especificados")
            return
        fich, fkey = argv[2], argv[3]
        fsaida = fich + ".enc"
        cifrar_ficheiro(fich, fkey, fsaida)
        print("Ficheiro cifrado em", fsaida)

    elif operacao == "dec":
        if not argv[2] or not argv[3]:
            print("Erro: ficheiro cifrado e chave não especificados")
            return
        fich, fkey = argv[2], argv[3]
        fsaida = fich.split(".")[0] + ".txt.dec"
        decifrar_ficheiro(fich, fkey, fsaida)
        print("Ficheiro decifrado em", fsaida)

    else:
        print("Erro: operação inválida")


if __name__ == "__main__":
    main(sys.argv)
