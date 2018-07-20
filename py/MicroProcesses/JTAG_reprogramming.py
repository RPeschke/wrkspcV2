#!/usr/bin/env python
import sys
import os
sys.path.append( os.getcwd()+'/lib/' )
import FileHandshake

'''
This Microprocess waits and watches for a file called
temp/handshake.txt to show up then executes its instructions.
When finished, temp/handshake.txt will be removed.
Whichever program generated temp/handshake.txt will
see that it's been removed and will resume its own
instructions.
'''


def progFPGA():
    print("Reprogramming FPGA . . .")
    os.system("sudo /bin/bash setup_thisMB.sh 0000000001")

hs = FileHandshake.FileHandshake()
while(1):
    print "Waiting for handshake . . ."
    hs.wait_for_handshake(progFPGA)
    print "Reprogramming of FPGA finished.\n"
