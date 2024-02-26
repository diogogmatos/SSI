import sys

def cesar(op, key, msg):
    if op == "enc":
        for i in range(len(msg)):
            if msg[i].isalpha():
                if msg[i].islower():
                    print(chr(ord(msg[i]) + key - 97), end="")
                else:
                    print(chr(ord(msg[i]) + key - 65), end="")
            else:
                print(chr(ord(msg[i]) + key - 65), end="")
    elif op == "dec":
        for i in range(len(msg)):
            if msg[i].isalpha():
                if msg[i].islower():
                    print(chr(ord(msg[i]) - key + 97), end="")
                else:
                    print(chr(ord(msg[i]) - key + 65), end="")
            else:
                print(chr(ord(msg[i]) - key + 65), end="")

def main():
    if len(sys.argv) != 4:
        print("Usage: python cesar.py <enc|dec> <key> <message>")
        sys.exit(1)

    op = sys.argv[1]
    key = ord(sys.argv[2])
    msg = sys.argv[3]
    print(op, key, msg)
    cesar(op, key, msg)
    print()

if __name__ == "__main__":
    main()