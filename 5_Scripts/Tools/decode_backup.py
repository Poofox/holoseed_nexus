#!/usr/bin/env python3
"""Decrypt ColorNote backup file"""

import hashlib
import sys
from Crypto.Cipher import AES

def derive_key_iv(password: str, salt: bytes):
    """OpenSSL EVP_BytesToKey style derivation"""
    pw = password.encode('utf-8')

    # First hash = key
    key = hashlib.md5(pw + salt).digest()

    # Second hash = IV
    iv = hashlib.md5(key + pw + salt).digest()

    return key, iv

def unpad(data):
    """PKCS7 unpad"""
    pad_len = data[-1]
    return data[:-pad_len]

def decrypt_colornote(input_file, password="0000", offset=28):
    """Decrypt ColorNote backup"""
    salt = b"ColorNote Fixed Salt"

    with open(input_file, 'rb') as f:
        data = f.read()

    encrypted = data[offset:]
    key, iv = derive_key_iv(password, salt)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)

    try:
        decrypted = unpad(decrypted)
    except:
        pass

    return decrypted

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "1.backup"
    password = sys.argv[2] if len(sys.argv) > 2 else "0000"

    result = decrypt_colornote(input_file, password)

    # Try to decode as UTF-8, show first 2000 chars
    try:
        text = result.decode('utf-8', errors='replace')
        print(f"Decrypted {len(result)} bytes with password '{password}':")
        print(text[:2000])
    except:
        print(f"Decrypted {len(result)} bytes (binary)")
        print(result[:500])
