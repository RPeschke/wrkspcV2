#!/usr/bin/env python
'''
OVERVIEW:
Ethernet Driver for sending UDP Packets.

AUTHORS:
Bronson Edralin <bedralin@hawaii.edu>
University of Hawaii at Manoa
Instrumentation Development Lab (IDLab), WAT214
'''

import sys, time
import socket
import select
import binascii

SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
FATAL      =  "\033[1;91m"
BCYAN      =  "\033[1;96m"
def Print(s,c):
    print"%s%s\033[m"%(c,str(s))

def asciiToHex(s):
    ''' Input:  s = string of ASCII chars
        Output: return string of HEX       '''
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)

    return reduce(lambda x,y:x+y, lst)

def hexToAscii(s):
    ''' Input:  s = string of HEX
        Output: return string of ASCII chars  '''
    return binascii.unhexlify(s) # actually converts hex string into binary data;
        # but the HEX codes for ASCII will convert it to ASCII

def hexToBin(s):
    ''' Input:  s = string of HEX
        Output: return binary data  '''
    return binascii.unhexlify(s)



class UDP:
    ''' class used to send/receive UDP packets over Ethernet '''
    def __init__(self, addr_fpga, port_fpga, addr_pc, port_pc, interface):
        self.DEBUG = 0
        self.addr_fpga = addr_fpga
        x = addr_fpga.split('.')
        self.addr_broadcast = x[0]+'.'+x[1]+'.'+x[2]+'.255'
        self.port_fpga = int(port_fpga)
        self.addr_pc = addr_pc
        self.port_pc = int(port_pc)
        self.interface = interface
        self.syncwd="000000010253594e4300000000"

        ''' socket for transmitting (broadcast) '''
        # set up socket for UDP Protocol
        self.sock_trans = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set to broadcast mode
        self.sock_trans.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#        self.sock_trans.setsockopt(socket.SOL_SOCKET, 25, self.interface)
        #self.sock_trans.setblocking(0)    # necessary for UDP

        # bind to all addr at this port
        #self.sock_trans.bind(('',self.port_fpga))

        ''' socket for receiving '''
        # set up socket for UDP Protocol
        self.sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set interface
#        self.sock_rcv.setsockopt(socket.SOL_SOCKET, 25, self.interface)
        self.sock_rcv.setblocking(0)    # necessary for UDP
        # bind to all addr at this port
        self.sock_rcv.bind(('',self.port_pc))

    def KLMprint(self, s, d="Packet Content"): # used to decode a UDP packet and print to terminal
            ##    Input: s = string of HEX
            ##           d = description
            ##    Output: Device, register No., 16-bit binary word
        Print( d.center(42, "-"), SOFT) # packet heading, user specified
        if (s[0:26] == self.syncwd): #remove syncword if present
            s = s[26:]
        # convert packet into 8-char-word list
        wlst = map(''.join, zip(*[iter(s)]*8))
        # convert last for characters of each word into binary
        bits = [bin(int(entry[4], 16))[2:].zfill(4)+" "+bin(int(entry[5], 16))[2:].zfill(4)+" "+bin(int(entry[6], 16))[2:].zfill(4)+" "+bin(int(entry[7], 16))[2:].zfill(4)+" " for entry in wlst]
        for i in range(len(wlst)):
            if   (wlst[i][0:2] == "AE" or wlst[i][0:2] == "ae"):
                Print("%s:\tWait %d" % (str(wlst[i]),int(wlst[i][4:8], 16)), SOFT)
            elif (wlst[i][0:2] == "AF" or wlst[i][0:2] == "af"):
                Print("%s:\tSCROD  Register: %-4d  %s  (%d)" % (str(wlst[i]),int(wlst[i][2:4], 16), bits[i], int(wlst[i][4:8], 16)), SOFT)
            elif (wlst[i][0:2] == "C0" or wlst[i][0:2] == "c0"):
                Print("%s:\tHV, ASIC: %d, Ch: %-2d trimDAC: %d" % (str(wlst[i]),int(wlst[i][2], 16), int(wlst[i][3], 16), int(wlst[i][6:8], 16)), SOFT)
            elif (wlst[i][0]   == "B"  or wlst[i][0]   == "b"):
                Print("%s:\tASIC_%s Register: %-4d  %s  (%d)" % (str(wlst[i]),wlst[i][1], int(wlst[i][2:4], 16), bits[i], int(wlst[i][4:8], 16)), SOFT)
            else:
                Print("(other) HEX word: %s" % wlst[i], SOFT)
        print

    # broadcast send
    def send(self, data):
        ''' Input:  data = data in HEX string w/ no spaces
            Output: returns nothing '''

        # Convert to binary data in format '\x##'
        data_bin = binascii.unhexlify(data)
        if (self.DEBUG):
            Print( "\n----------------------------------------------------------", SOFT)
            Print( "Transmit to Addr: '%s'" % str("("+\
                str(self.addr_broadcast)+", "+str(self.port_fpga)+")\n"), SOFT)
            Print( "Transmit "+str(len(data)/2)+" bytes of data\n", SOFT)
            self.KLMprint(data)
            #print ""
        #data = hexToAscii(data)  # Convert HEX to ASCII so we can send
        #if (self.DEBUG):
        #    print "Transmit UDP in ASCII is: ",data
            Print( "----------------------------------------------------------\n", SOFT)
        self.sock_trans.sendto(data_bin, (self.addr_broadcast, self.port_fpga))
        #self.sock_rcv.sendto(data_bin, (self.addr_fpga, self.port_fpga))

    def receive(self, bufferSize):
        ''' Input:  bufferSize = buffer size for receive
            Output: returns data in HEX                  '''
        CONNECTION_LIST = []
        done = False

        #CONNECTION_LIST = []
        #CONNECTION_LIST.append(self.sock_rcv)
        while(not done):
            CONNECTION_LIST = []
            CONNECTION_LIST.append(self.sock_rcv)
            inputrdy, outputrdy, exceptrdy = select.select(CONNECTION_LIST, [], [])

            for i in inputrdy:
                if inputrdy is self.sock_rcv:
                    sockfd, addr = self.sock_rcv.accept()
                    CONNECTION_LIST.append(sockfd)
                    #if (self.DEBUG): Print( "Connected to ( %s, %s)" % (sockfd, addr), SOFT)
                    pass
                else:
                    try:
                        data, addr = i.recvfrom(int(bufferSize))
                        if (self.DEBUG):
                            Print( "\n----------------------------------------------------------", SOFT)
                            Print( "Recv from Addr: '%s'\n" % str(addr), SOFT)

                        # necessary to make a string of hex
                        #data_ascii = data.decode('utf-8')
                        #data_ascii = data.decode('cp1252')
                        data_hex = binascii.b2a_hex(data)  # Convert binary data to hex string
                        #data_hex = asciiToHex(data_ascii)

                        if (self.DEBUG):
                            #print "Recv UDP in ASCII: ", data_ascii
                            #print ""
                            Print( "Received %s bytes of data\n" % (str(len(data_hex)/2)), SOFT)
                            Print( "Recv UDP in HEX: ", SOFT)
                            self.KLMprint(data_hex)
                            Print( "----------------------------------------------------------\n", SOFT)
                        done = True
                    except Exception, e:
                        Print("Error!!! %s" % e, FATAL)
                        i.close()
                        CONNECTION_LIST.remove(i)
                        #CONNECTION_LIST.append(self.sock_rcv)
                        self.open()
        return data_hex

    def readReg(self,RegNo):
        buffSize=3000;
        cmd1=hex(int('AD000000',16) | RegNo*(2**16)).split('x')[1];
        self.send(self.syncwd+cmd1);
        rcv = self.receive(buffSize);
        idx=rcv.find("7363726f644135307374617473796e63ac");
        if (self.DEBUG): Print( "Received HEX: %s" % str(rcv[34:36]), SOFT)
        if (idx==-1):
            Print( (rcv), SOFT)
            Print( "Unknown package recieved from SCROD- exiting!", FATAL)
            exit(-1)
        if int(rcv[34:36],16)!=RegNo:
            Print( "RX package does not match TX request- exiting!", FATAL)
            exit(-1)
        #print(rcv[36:40])
        return int(rcv[36:40],16)

    def readRegs(self,RegNoS,RegNoE):# read a block of registers from RegNoS start to RegNoE end inclusive
        RegRange=(RegNoE-RegNoS); # plus 1 b/c always counting from zero, e.g. 19-10 = 9, but 10 thru 19 is 10 entries ## RegRange added by CK 8/1/17
        buffSize=3000;
        val=[0 for i in range(RegRange)];
        cmd1=hex(int('AD000000',16) | RegNoE*(2**8) | RegNoS).split('x')[1];
        self.send(self.syncwd+cmd1);
        rcv = self.receive(buffSize);
        idx=rcv.find("7363726f644135307374617473796e63");
        #print "Received HEX: ",rcv[34:36]
        if (idx==-1):
           Print( ("Unknown Header recieved from SCROD- exiting!"), FATAL)
           exit(-1)
        for I in range (RegNoS,RegNoE):
#          print rcv[(32+8*(I-RegNoS)):(40+8*(I-RegNoS))];
          if rcv[(32+8*(I-RegNoS)):(34+8*(I-RegNoS))]!="ac":
               Print( "Unknown Package recieved from SCROD- exiting!", FATAL)
               exit(-1)
          if int(rcv[(34+8*(I-RegNoS)):(36+8*(I-RegNoS))],16)!=I:
               Print( "RX package does not match TX request- exiting!", FATAL)
               exit(-1)
          val[I-RegNoS]=int(rcv[(36+8*(I-RegNoS)):(40+8*(I-RegNoS))],16)
#          if int(rcv[32:34],16)!=RegNo:
#              print ("RX package does not match TX request- exiting!")
#              exit(-1)
        #print(rcv[36:40])
        return val

    def close(self):
        ''' Input:  nothing
            Output: return nothing just closes socket  '''
        #self.sock_rcv.shutdown(socket.SHUT_RDWR)
        self.sock_rcv.close()
        #self.sock_trans.shutdown(socket.SHUT_RDWR)
        self.sock_trans.close()

    def open(self):
        ''' socket for transmitting (broadcast) '''
        # set up socket for UDP Protocol
        self.sock_trans = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set to broadcast mode
        self.sock_trans.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #self.sock_trans.setsockopt(socket.SOL_SOCKET, 25, self.interface)
        #self.sock_trans.setblocking(0)    # necessary for UDP

        # bind to all addr at this port
        self.sock_trans.bind(('',self.port_fpga))

        ''' socket for receiving '''
        # set up socket for UDP Protocol
        self.sock_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set interface
#        self.sock_rcv.setsockopt(socket.SOL_SOCKET, 25, self.interface)
        self.sock_rcv.setblocking(0)    # necessary for UDP
        self.sock_rcv.bind(('',self.port_pc))
        # bind to all addr at this port
