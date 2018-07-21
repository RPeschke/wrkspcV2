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

NORM       =  "\033[m"
BOLD       =  "\033[1m"
FAINT      =  "\033[2m"
SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
WARNING    =  "\033[93m"
FATAL      =  "\033[1;91m"
UNDERLINE  =  "\033[4m"
BCYAN      =  "\033[1;96m"
BROWN      =  "\033[33m"
def Print(c,s):
    print"%s%s%s"%(c,str(s),NORM)
DEBUG = 0

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
        self.addr_fpga = addr_fpga
        x = addr_fpga.split('.')
        self.addr_broadcast = x[0]+'.'+x[1]+'.'+x[2]+'.255'
        self.port_fpga = int(port_fpga)
        self.addr_pc = addr_pc
        self.port_pc = int(port_pc)
        self.interface = interface

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

    # broadcast send
    def send(self, data):
        ''' Input:  data = data in HEX string w/ no spaces
            Output: returns nothing '''

        # Convert to binary data in format '\x##'
        data_bin = binascii.unhexlify(data)
        if DEBUG:
            print "\n----------------------------------------------------------"
            print "Transmit to Addr: '%s'" % str("("+\
                str(self.addr_broadcast)+", "+str(self.port_fpga)+")")
            print ""
            print "Transmit "+str(len(data)/2)+" bytes of data"
            print ""
            print "Transmit UDP in HEX is: ",data
            #print ""
        #data = hexToAscii(data)  # Convert HEX to ASCII so we can send
        #if DEBUG:
        #    print "Transmit UDP in ASCII is: ",data
            print "----------------------------------------------------------\n"
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
                    print "Connected to ( %s, %s)" %(addr)
                    pass
                else:
                    try:
                        data, addr = i.recvfrom(int(bufferSize))
                        if DEBUG:
                            print "\n----------------------------------------------------------"
                            print "Recv from Addr: '%s'" %str(addr)
                            print ""

                        # necessary to make a string of hex
                        #data_ascii = data.decode('utf-8')
                        #data_ascii = data.decode('cp1252')
                        data_hex = binascii.b2a_hex(data)  # Convert binary data to hex string
                        #data_hex = asciiToHex(data_ascii)

                        if DEBUG:
                            #print "Recv UDP in ASCII: ", data_ascii
                            #print ""
                            print "Received "+str(len(data_hex)/2)+" bytes of data"
                            print ""
                            print "Recv UDP in HEX: ",data_hex
                            print "----------------------------------------------------------\n"
                        done = True
                    except Exception, e:
                        Print(FATAL,"Error!!! %s" % e)
                        i.close()
                        CONNECTION_LIST.remove(i)
                        #CONNECTION_LIST.append(self.sock_rcv)
                        self.open()
        return data_hex

    def readReg(self,RegNo):
        syncwd="000000010253594e4300000000";
        buffSize=3000;
        cmd1=hex(int('AD000000',16) | RegNo*(2**16)).split('x')[1];
        self.send(syncwd+cmd1);
        rcv = self.receive(buffSize);
        idx=rcv.find("7363726f644135307374617473796e63ac");
        #print "Received HEX: ",rcv[34:36]
        if (idx==-1):
            print (rcv)
            print ("Unknown package recieved from SCROD- exiting!")
            exit(-1)
        if int(rcv[34:36],16)!=RegNo:
            print ("RX package does not match TX request- exiting!")
            exit(-1)
        #print(rcv[36:40])
        return int(rcv[36:40],16)

    def readRegs(self,RegNoS,RegNoE):# read a block of registers from RegNoS start to RegNoE end inclusive
        RegRange=(RegNoE-RegNoS); # plus 1 b/c always counting from zero, e.g. 19-10 = 9, but 10 thru 19 is 10 entries ## RegRange added by CK 8/1/17
        syncwd="000000010253594e4300000000";
        buffSize=3000;
        val=[0 for i in range(RegRange)];
        cmd1=hex(int('AD000000',16) | RegNoE*(2**8) | RegNoS).split('x')[1];
        self.send(syncwd+cmd1);
        rcv = self.receive(buffSize);
        idx=rcv.find("7363726f644135307374617473796e63");
        #print "Received HEX: ",rcv[34:36]
        if (idx==-1):
           print ("Unknown Header recieved from SCROD- exiting!")
           exit(-1)
        for I in range (RegNoS,RegNoE):
#          print rcv[(32+8*(I-RegNoS)):(40+8*(I-RegNoS))];
          if rcv[(32+8*(I-RegNoS)):(34+8*(I-RegNoS))]!="ac":
               print ("Unknown Package recieved from SCROD- exiting!")
               exit(-1)
          if int(rcv[(34+8*(I-RegNoS)):(36+8*(I-RegNoS))],16)!=I:
               print ("RX package does not match TX request- exiting!")
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
