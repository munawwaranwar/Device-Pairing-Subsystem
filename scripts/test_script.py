import sys
from urllib.parse import quote, unquote
import requests

def main():
    text = "11%2BPAKISTAN"
    a = unquote(text)
    b = quote(a)
    print(a,b)

if __name__ == "__main__":
    main()
