#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/L1ghtM4n

# Import modules
from io import BytesIO
from threading import Lock
from typing import Iterator
from hashlib import pbkdf2_hmac
# Import packages
from .options import ContainerOptions
from .partitions import Partition, \
    SPLITTER_PART, SPLITTER_DATA, \
    form_partition, form_empty_zip
from .errors import \
    PartitionNotFound, PartitionAlreadyExists

# Create lock to prevent some bugs
lock = Lock()

""" Container object """
class CryptoContainer(object):
    def __init__(self, filename, options:ContainerOptions=ContainerOptions()):
        self.options = options
        self.filename = filename
        # Opened partitions
        self.opened_partitions = []
        try: # Try read container content
            data = open(filename, "rb").read()
        except FileNotFoundError:
            self.handle = BytesIO()
        else:
            self.handle = BytesIO(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    """ Get sha512 hash bytes from key """
    def __to_hash(self, key:bytes) -> bytes:
        return pbkdf2_hmac(
            password=key,
            hash_name="sha512",
            salt=self.options.salt,
            dklen=self.options.dklen,
            iterations=self.options.iterations,
        )

    """ Create partition in container """
    def create_partition(self, key:bytes) -> Partition:
        # Acquire lock
        lock.acquire(True)
        # Read content, get zip bytes, hash key
        content = self.handle.read()
        empty_zip = form_empty_zip(key)
        hashed_key = self.__to_hash(key)
        # Partition already exists exception
        if hashed_key in content:
            raise PartitionAlreadyExists("Partition already exists")
        # Create new partition
        partition = form_partition(hashed_key, empty_zip)
        # Write new data to file
        self.handle.write(content + partition)
        # Release lock
        lock.release()
        # Return partition
        return self.open_partition(key)

    """ Open partition from container """
    def open_partition(self, key:bytes) -> Partition:
        # Acquire lock
        lock.acquire(True)
        hashed_key = self.__to_hash(key)
        # Find partition in container
        for partition in self.__iterate_partitions(key):
            if partition.key_hash == hashed_key:
                # Add partition to opened partitions list
                if partition not in self.opened_partitions:
                    self.opened_partitions.append(partition)
                # Release lock
                lock.release()
                return partition
        # Release lock
        lock.release()
        # Failed read partition
        raise PartitionNotFound("Partition not exists")

    """ Delete partition from container """
    def erase_partition(self, partition_obj:Partition):
        # Acquire lock
        lock.acquire(True)
        # New buffer
        updated_partitions = BytesIO()
        # Get partitions
        partitions = self.handle.read().split(SPLITTER_PART)
        for partition in partitions:
            # Empty or invalid partition
            if SPLITTER_DATA not in partition:
                continue
            # Get key hash and zip bytes
            key, zip = partition.split(SPLITTER_DATA)
            # Check key with partition key
            if partition_obj.key_hash == key:
                continue # Skip selected partition
            # Write old partition
            old_partition = form_partition(key, zip)
            updated_partitions.write(old_partition)
        # Release lock
        lock.release()
        # Return changes
        self.handle = updated_partitions

    """ Save partition in container """
    def save_partition(self, partition_obj:Partition):
        # New buffer
        updated_partitions = BytesIO()
        # Get partitions
        partitions = self.handle.getvalue().split(SPLITTER_PART)
        for partition in partitions:
            # Empty or invalid partition
            if SPLITTER_DATA not in partition:
                continue
            # Get key hash and zip bytes
            key, zip = partition.split(SPLITTER_DATA)
            # Check key with partition key
            if partition_obj.key_hash == key:
                new_zip = partition_obj.close()
                new_partition = form_partition(key, new_zip)
                # Write new partition
                updated_partitions.write(new_partition)
                continue
            # Write old partition
            old_partition = form_partition(key, zip)
            updated_partitions.write(old_partition)
        # Return changes
        self.handle = updated_partitions

    """ Check if partition exists """
    def contains_partition(self, key:bytes) -> bool:
        hashed_key = self.__to_hash(key)
        for partition_obj in self.__iterate_partitions(key):
            if partition_obj.key_hash == hashed_key:
                return True
        return False

    """ Get partitions list in container """
    def __iterate_partitions(self, key:bytes) -> Iterator[Partition]:
        # Get partitions
        partitions = self.handle.getvalue().split(SPLITTER_PART)
        for partition in partitions:
            # Empty or invalid partition
            if SPLITTER_DATA not in partition:
                continue
            # Get key hash and zip bytes
            key_hash, zip = partition.split(SPLITTER_DATA)
            # Check hash length
            if len(key_hash) == self.options.dklen:
                yield Partition(key=key, key_hash=key_hash, zip_buffer=zip)

    """ Save changes in container file """
    def close(self):
        # Acquire lock
        lock.acquire(True)
        # Save all opened partitions
        for partition in self.opened_partitions:
            self.save_partition(partition)
            self.opened_partitions.remove(partition)
        # Save container
        with open(self.filename, "wb") as container:
            container.write(self.handle.getvalue())
        # Release lock
        lock.release()

