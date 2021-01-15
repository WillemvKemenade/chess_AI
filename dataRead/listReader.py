# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 16:43:22 2021

@author: erikv
"""
import json

def write(l,filename):
    with open(filename, 'w') as filehandle:
        json.dump(l, filehandle)

def read(filename):
    with open(filename, 'r') as filehandle:
        l = json.load(filehandle)
    return l
    

