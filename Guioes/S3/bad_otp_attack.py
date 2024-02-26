import random
import sys

def bad_prng(n):
    """ an INSECURE pseudo-random number generator """
    random.seed(random.randbytes(2))
    return random.randbytes(n)

def decrypt_with_otp(encrypted_text, otp):
    decrypted_text = ""
    for i in range(len(encrypted_text)):
        decrypted_char = chr(encrypted_text[i] ^ otp[i % len(otp)])
        decrypted_text += decrypted_char
    return decrypted_text

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 bad_otp_attack.py <encrypted_file> <word1> <word2> ...")
        sys.exit(1)

    encrypted_file = sys.argv[1]
    words = sys.argv[2:]

    with open(encrypted_file, "rb") as f:
        encrypted_text = f.read()
    for word in words:
        for i in range(len(encrypted_text)):
            otp_candidate = bytes([encrypted_text[i] ^ ord(word[i % len(word)])])
            decrypted_text = decrypt_with_otp(encrypted_text, otp_candidate)
            if word in decrypted_text:
                print("Found matching word:", word)
                print("Decrypted text:", decrypted_text)
                break
    else:
        print("No matching word found in decrypted text.")

if __name__ == "__main__":
    main()
