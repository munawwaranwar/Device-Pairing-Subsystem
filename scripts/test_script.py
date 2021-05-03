import sys
from urllib.parse import quote, unquote
import requests

def main():
    text = "11%2BPAKISTAN"
    a = unquote(text)
    b = quote(a)
    print(a,b)

    text2 = "123|abc"
    c = quote(text2)
    print(c)


if __name__ == "__main__":
    main()
