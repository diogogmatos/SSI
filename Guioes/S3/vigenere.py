import sys

def encrypt_vigenere(plain_text, key):
    encrypted_text = ""
    key_index = 0
    for char in plain_text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)].upper()) - ord('A')
            if char.islower():
                encrypted_char = chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))
            else:
                encrypted_char = chr(((ord(char) - ord('A') + shift) % 26) + ord('A'))
            encrypted_text += encrypted_char
            key_index += 1
        else:
            encrypted_text += char
    return encrypted_text

def decrypt_vigenere(encrypted_text, key):
    decrypted_text = ""
    key_index = 0
    for char in encrypted_text:
        if char.isalpha():
            shift = ord(key[key_index % len(key)].upper()) - ord('A')
            if char.islower():
                decrypted_char = chr(((ord(char) - ord('a') - shift + 26) % 26) + ord('a'))
            else:
                decrypted_char = chr(((ord(char) - ord('A') - shift + 26) % 26) + ord('A'))
            decrypted_text += decrypted_char
            key_index += 1
        else:
            decrypted_text += char
    return decrypted_text

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 vigenere.py <enc/dec> <key> <text>")
        sys.exit(1)

    action = sys.argv[1].lower()
    key = sys.argv[2].upper()
    text = sys.argv[3]

    if action == "enc":
        result = encrypt_vigenere(text, key)
    elif action == "dec":
        result = decrypt_vigenere(text, key)
    else:
        print("Invalid action. Please use 'enc' for encryption or 'dec' for decryption.")
        sys.exit(1)

    print("Result:", result)

if __name__ == "__main__":
    main()
