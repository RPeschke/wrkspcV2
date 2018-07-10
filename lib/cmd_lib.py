#!/usr/bin/env python
'''
OVERVIEW:
Ethernet Driver for sending UDP Packets.

AUTHORS:
Bronson Edralin <bedralin@hawaii.edu>
University of Hawaii at Manoa
Instrumentation Development Lab (IDLab), WAT214
'''

import sys
import time
import os
import csv

DEBUG = 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[96m'
    BROWN = '\033[33m'


class CMD:
    ''' class used to generate UDP packets for sending over ethernet '''
    def __init__(self, SN, rawHV, ASICmask):
        self.SN = SN
        self.rawHV = rawHV
        self.ASICmask = ASICmask
        self.syncwd = "000000010253594e4300000000"
        self.forceTrig = self.syncwd + "AF00FFFF"+"AF00FFFF"+"AF370001"+"AE000001"+"AF370000"+"AE000001"+"AF320001"+"AE000001"+"AF320000" # modified original from AF00FFF+AF00FFFFF / CK
        self.turnOffASICtriggering = self.syncwd + "AF270000" + "AE000100"

    def KLMprint(self, s, d): # used to decode a UDP packet and print to terminal
        ''' Input: s = string of HEX
                   d = description
            Output: Device, register No., 16-bit binary word '''
        print d.center(42, "-") # packet heading, user specified
        if (s[0:26] == self.syncwd): #remove syncword if present
            s = s[26:]
        # convert packet into 8-char-word list
        wlst = map(''.join, zip(*[iter(s)]*8))
        # convert last for characters of each word into binary
        bits = [bin(int(entry[4], 16))[2:].zfill(4)+" "+bin(int(entry[5], 16))[2:].zfill(4)+" "+bin(int(entry[6], 16))[2:].zfill(4)+" "+bin(int(entry[7], 16))[2:].zfill(4)+" " for entry in wlst]
        for i in range(len(wlst)):
            if   (wlst[i][0:2] == "AE" or wlst[i][0:2] == "ae"):
                print "Wait %d" % int(wlst[i][4:8], 16)
            elif (wlst[i][0:2] == "AF" or wlst[i][0:2] == "af"):
                print "SCROD  Register: %-4d  %s  (%d)" % (int(wlst[i][2:4], 16), bits[i], int(wlst[i][4:8], 16))
            elif (wlst[i][0:2] == "C0" or wlst[i][0:2] == "c0"):
                print "HV, ASIC: %d, Ch: %-2d trimDAC: %d" % (int(wlst[i][2], 16), int(wlst[i][3], 16), int(wlst[i][6:8], 16))
            elif (wlst[i][0]   == "B"  or wlst[i][0]   == "b"):
                print "ASIC_%s Register: %-4d  %s  (%d)" % (wlst[i][1], int(wlst[i][2:4], 16), bits[i], int(wlst[i][4:8], 16))
            else:
                print "(other) HEX word: %s" % wlst[i]
        print

    def Get_ASIC_HV_from_file(self, ASIC):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.rawHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            print "Could not find calibration file %s! Exiting . . ." % calib_file
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            print "Calibration file %s has wrong number of lines. Exiting!" % calib_file
            print "Remove faulty calibration file and rerun script."
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        hvList = [int(line[1]) for line in fileLines]
        print "Found HV starting values and threshold base values from calibration file."
        print hvList
        print
        return hvList

    def Get_ASIC_TH_from_file(self, ASIC):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.rawHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            print "Could not find calibration file %s! Exiting . . ." % calib_file
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            print "Calibration file %s has wrong number of lines. Exiting!" % calib_file
            print "Remove faulty calibration file and rerun script."
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        thBase = [int(line[0]) for line in fileLines]
        print "Found threshold base values from calibration file."
        print thBase
        print
        return thBase

    def Generate_ASIC_triggered_run_config_cmd(self, opMode, outMode, winOffset):
        cmd  = self.syncwd + "AF250000" + "AE000100"#disable ext. trig
        cmd += "AF3E0000" + "AE000100"# win start set to zero for internal triggering
        cmd += hex(int('AF360000',16) | 0              | winOffset              ).split('x')[1] +"AE000100"#set win offset
        cmd += hex(int('AF330000',16) | 0              | int(self.ASICmask,2)   ).split('x')[1] +"AE000100"#set asic number
        cmd += hex(int('AF260000',16) | opMode*(2**12) | 2**7                   ).split('x')[1] +"AE000100"#CMDREG_PedDemuxFifoOutputSelect(13 downto 12)-->either wavfifo or pedfifo,CMDREG_PedSubCalcMode(10 downto 7)-->currently only using bit 7: 1 for peaks 2 for troughs, sample offset is 3400 o6 600 respectively
        cmd += hex(int('AF270000',16) | 1*(2**15)      | int(self.ASICmask,2)   ).split('x')[1] +"AE000100"#set trig mode & asic trig enable
        cmd += hex(int('AF4A0000',16) | outMode*(2**8) | 1*2**4 + 2*2**0        ).split('x')[1] +"AE000100"#set outmode and win boundaries for trigger bits: x12 scans 1 win back and two forward
        cmd += "AF4F0002" # external trigger bit format
        return cmd

    def Generate_Software_triggered_run_config_cmd(self, opMode,  outMode, ASIC):
        cmd  = self.syncwd
        cmd += "AF250000" + "AE000100" # disable ext. trig
        cmd += hex(int('AF330000',16) | 2**ASIC             ).split('x')[1] +"AE000100" # set asic number
        cmd += "AF3E8000"+"AE000100" # set win start
        cmd += hex(int('AF250000',16)                       ).split('x')[1] +"AE000100"
        cmd += hex(int('AF270000',16) | 2**ASIC             ).split('x')[1] +"AE000100" # set trig mode & asic trig enable
        cmd += "AF360000" +"AE000100" # set win offset to zero
        cmd += hex(int('AF260000',16) | opMode*(2**12)      ).split('x')[1] +"AE000100" # CMDREG_PedDemuxFifoOutputSelect(13 downto 12)-->either wavfifo or pedfifo,CMDREG_PedSubCalcMode(10 downto 7)-->currently only using bit 7: 1 for peaks 2 for troughs, sample offset is 3400 o6 600 respectively
        cmd += hex(int('AF4A0000',16) | outMode*(2**8) | 18 ).split('x')[1] +"AE000100" # set outmode and win boundaries for trigger bits: x12 scans 1 win back and two forward
        cmd += "AF4F0000" # external trigger bit format
        return cmd

    def Set_Readout_Window(self, win):
        if (win<0 | win>511):
            print "Invalid window number: (%d)" % win
            print "Exiting . . ."
            exit(-1)
        cmd = self.syncwd + hex(int('AF3E8000',16) | win).split('x')[1]
        return cmd

    def Generate_ASIC_HV_cmd(self, ASIC, chHV_list):
        cmd = self.syncwd
        for ch in range(len(chHV_list)):
            cmd += hex( int('C',16)*(2**28) | ASIC*(2**20) | (ch)*(2**16) | chHV_list[ch] ).split('x')[1]
        return cmd

    def Generate_ASIC_TH_cmd(self, ASIC, chTh_list):
        cmd = self.syncwd
        for ch in range(len(chTh_list)):
            cmd += hex( int('B',16)*(2**28) | ASIC*(2**24) | (2*ch)*(2**16) | chTh_list[ch] ).split('x')[1]
        return cmd
