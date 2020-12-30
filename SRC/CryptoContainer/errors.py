#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/L1ghtM4n


"""
When a user tries to open a partition that is not exists in the container
"""
class PartitionNotFound(Exception):
    pass

"""
When a user tries to create a partition that already exists
"""
class PartitionAlreadyExists(Exception):
    pass
