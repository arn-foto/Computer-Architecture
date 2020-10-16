#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *
from os import listdir

cpu = CPU()
file_list = {f:None for f in listdir("examples")}

if len(sys.argv) > 1:
    file_name = sys.argv[1]
    if file_name in file_list:
        cpu.load(file_name)
    else:
        print("invalid file name")
        sys.exit(1)
else:
    cpu.load("sctest.ls8")
        
        
# cpu.load()
cpu.run()
# print(file_list)