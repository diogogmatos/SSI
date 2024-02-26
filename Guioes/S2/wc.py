import sys

# defs auxiliares...
def main(inp: list[str]):
    file = open(inp[1])
    file_str = file.read()
    words = len(file_str.split())
    rows = len(file_str.split("\n"))
    chars = len(file_str)
    print(rows, words, chars)

# Se for chamada como script...
if __name__ == "__main__":
    main(sys.argv)
