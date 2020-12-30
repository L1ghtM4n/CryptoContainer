#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/L1ghtM4n

# Import modules (pip install pycryptodome)
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

""" AES-CBC 128bit (16 bytes key) """
class AESCipher:
    def __init__(self, key):
        self.key = key
        if len(key) != 16:
            raise ValueError("Key length must be 16")

    def encrypt(self, data: bytes) -> bytes:
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(pad(data, AES.block_size))

    def decrypt(self, data: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, data[:AES.block_size])
        return unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)

