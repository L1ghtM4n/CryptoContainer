#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/L1ghtM4n

# Import modules
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
# Import packages
from .encryption import AESCipher

# Splitters
SPLITTER_DATA = b'.' * 6
SPLITTER_PART = b'.' * 12

""" Create encrypted empty zip """
def form_empty_zip(key:bytes) -> bytes:
    io = BytesIO()
    ZipFile(io, "a").close()
    buffer = io.getvalue()
    empty_zip = AESCipher(key).encrypt(buffer)
    return empty_zip

""" Create partition """
def form_partition(hashed_key:bytes, zip_buffer:bytes) -> bytes:
    # Create partition
    return (b''
            + hashed_key    # Hashed key (128 bytes)
            + SPLITTER_DATA # Splitter (6 empty bytes)
            + zip_buffer    # Empty zip file bytes
            + SPLITTER_PART # Splitter (12 empty bytes)
        )

""" Partition object """
class Partition(object):
    def __init__(self, key:bytes, key_hash:bytes, zip_buffer:bytes):
        self.key_hash = key_hash
        self.__cipher = AESCipher(key)
        self.__zip_buffer = (zip_buffer[1:] if zip_buffer[0] == 32 else zip_buffer)
        self.__io = BytesIO(self.__cipher.decrypt(self.__zip_buffer))
        self.handle = ZipFile(self.__io, "a", ZIP_DEFLATED, False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self) -> str:
        size = len(self.__zip_buffer) + len(self.key_hash)
        return f"Partition (size={size})"

    # Export partition to zip file
    def export_zip(self, filename:str) -> str:
        self.handle.close()
        buff = self.__io.getvalue()
        with open(filename, "wb") as new_zip:
            new_zip.write(buff)
        return filename

    # Read zip buffer and encrypt
    def close(self) -> bytes:
        self.handle.close()
        buff = self.__io.getvalue()
        return self.__cipher.encrypt(buff)
