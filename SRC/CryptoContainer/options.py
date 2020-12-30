#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author github.com/L1ghtM4n

""" Hashing options object """
class ContainerOptions(object):
    def __init__(self, iterations:int=2205, salt:bytes=b"lightman"):
        self.iterations = iterations
        self.dklen = 128
        self.salt = salt
