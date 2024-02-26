import sys


def verify(msg, word1, word2):
    for j in range(26):
        word = ""
        for i in range(len(msg)):
                if msg[i].isalpha():
                    if msg[i].islower():
                        word += chr(ord(msg[i]) - (ord('a') + j) + 97)
                    else:
                        word += chr(ord(msg[i]) - (ord('A') + j) + 65)
                else:
                    word += chr(ord(msg[i]) - (ord('a') + j) + 65)
        if word1 in word or word2 in word:
            return (chr(ord('A') + j), word)
    return ("", "")


def main():
    if len(sys.argv) != 4:
        print("Usage: python cesar.py <enc|dec> <key> <message>")
        sys.exit(1)
    msg = sys.argv[1]
    word1 = sys.argv[2]
    word2 = sys.argv[3]
    (chave, palavra) = verify(msg, word1, word2)
    print(chave)
    print(palavra)

if __name__ == "__main__":
    main()