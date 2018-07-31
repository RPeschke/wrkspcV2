#!/usr/bin/env python
import sys, os, time, csv, numpy as np
from time import strftime
sys.path.append( os.getcwd() )
import linkEth, cmd_lib, FileHandshake
sys.path.append('/home/testbench2/root_6_08/lib')
import ROOT
ROOT.gROOT.LoadMacro("root/TTreeMgmt/WriteParametersToRootFile.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/PlotPedestalStatistics.cxx")
ROOT.gROOT.LoadMacro("root/TTreeMgmt/AveragePedestalTTree.cxx")

# Construct command and linkEth classes for building and sending hex packets to FPGA
ETH = linkEth.UDP('192.168.20.5', '24576', '192.168.20.1', '28672', "eth4") # (addr_fpga, port_fpga, addr_pc, port_pc, interface):

SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
FATAL      =  "\033[1;91m"
BCYAN      =  "\033[1;96m"
def Print(s,c):
    print"%s%s\033[m"%(c,str(s))

def CheckCmdLineArgs(sys):
    usageMSG=FATAL+"Usage:\n"+\
    "./SteeringScript.py <S/N> <HV>\n"+OKBLUE +\
    "Where:\n"+\
        "<S/N>          = KLMS_0XXX\n"+\
        "<HV>           = (e.g.) 74p52\n"
    if (len(sys.argv)!=3):
        Print(usageMSG,FATAL)
        exit(-1)

class ImportRunControlFunctions:
    def __init__(self, sys, DEBUG=0):
        CheckCmdLineArgs(sys)
        self.DEBUG = DEBUG
        if (self.DEBUG): ETH.DEBUG = 1

        ### ----initialize RUN parameters---- ###
        self.t0                = time.time()
        self.SN                = str(sys.argv[1])
        self.strHV             = str(sys.argv[2])
        self.rawHV             = float(self.strHV.replace("p","."))

        ### ----initialize FILE HANDLING variables---- ###
        self.date              = strftime("%Y%m%d", time.localtime())
        self.datetime          = strftime("%Y%m%d_%H%M%S%Z", time.localtime())
        self.binDatafile       = "temp/data.dat"
        self.root_file             = "data/%s/%s_%s.root" % (self.SN,self.SN,self.date)
        self.pedfile           = "data/%s/pedestals.root" % (self.SN)
        #self.root_file             = "data/%s/%s_%s.root" % (self.SN,self.SN,self.datetime)

        ### ----initialize CONTROL PARAMETERS to defaults---- ###
        self.NumEvts           = 0
        self.NumSoftwareEvtsPerWin = 0
        self.ASICmask          = "0000000001"  # e.g. 0000000111 for enabling ASICs 0, 1, and 2
        self.HVmask            = "0100000000000001" #16-ch mask: 0= 255 trim DAC counts, 1= HV DAC from file
        self.TrigMask          = "0000000000000001" #16-ch mask: 0= 4095 trig DAC counts, 1= trig DAC from file
        self.HVDAC_offset      = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        self.ThDAC_offset      = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]

        ### ----initialize TH and HV SCAN PARAMETERS to defaults---- ###
        self.targetFreq = 75
        self.HVscanTrigLevel = 30

        ### ----HARD-CODED CONTROL PARAMETERS---- ###
        self.ClkFreq           = 63.5e6
        self.ScalerCntNum16BitCycles = 10
        self.FWpedSubType      = 3 # 1 for FW pedSub, 2 for peds only, 3 for raw data
        self.ASIClookbackParam = 3
        self.FWoutMode         = 0 # 0 for waveforms, 1 for feat. ext. data only
        self.ParserPedSubType  = "-SWpeds"
        self.RunConfig = ""
        if not (os.path.isdir("data/"+self.SN)):
            os.system("mkdir -p data/" + self.SN + "/plots")

    def Get_ASIC_Th_from_file(self, ASIC, opt=""):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            Print("Could not find calibration file %s! Exiting . . ." % (calib_file),FATAL)
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            Print("Calibration file %s has wrong number of lines. Exiting!" % (calib_file),FATAL)
            Print("Remove faulty calibration file and rerun script" ,FATAL)
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        thBase = [int(line[0]) for line in fileLines]
        if not (opt=='quiet'):
            self.PrintThList(thBase)
        return thBase

    def PrintThList(self,ThList):
        Print("Found threshold base values from calibration file", SOFT)
        Print(ThList, OKGREEN)

    def Get_ASIC_HV_from_file(self, ASIC, opt=""):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isfile(calib_file)):  #infile.mode == 'r':
            Print("Could not find calibration file %s! Exiting . . ." % calib_file, FATAL)
            exit(-1)
        num_lines = int(os.popen("sed -n '$=' "+calib_file).read())
        if (num_lines == 15):
            infile = open(calib_file, 'r')
        else:
            Print("Calibration file %s has wrong number of lines. Exiting!" % (calib_file), FATAL)
            Print("Remove faulty calibration file and rerun calibration script", FATAL)
            quit()
        csvFile = csv.reader(infile, delimiter='\t')
        fileLines= []
        for line in csvFile:
            fileLines.append(line)
        infile.close()
        hvList = [int(line[1]) for line in fileLines]
        if not (opt=='quiet'):
            self.PrintHVList(hvList)
        return hvList

    def PrintHVList(self,hvList):
        Print("\nHV base for \033[94mtargetFreq = %dkHz\033[95m at \033[94mtrigLevel = %d DAC counts\033[95m:" % (self.targetFreq,self.HVscanTrigLevel),SOFT)
        Print(hvList, OKGREEN)

    def OpenEthLinkAndDataFile(self):
        if (self.DEBUG): Print("Opening port", SOFT)
        if (self.DEBUG): Print("Opening binary data file for writing", SOFT)
        ETH.open()
        f = open(self.binDatafile,'wb') #a=append, w=write, b=binary
        return f

    def CheckTimeSinceLastReprogram(self,tProg):
        return time.time()-tProg > 12600

    def MainDataCollectionLoop(self,cmd,f):
        if (self.DEBUG): Print("Sending run configuration to FPGA", SOFT)
        self.RunConfig = cmd.Generate_ASIC_triggered_run_config_cmd()
        ETH.send(self.RunConfig)
        tExtra = 0
        evtNum = 0
        tProg = t0 = time.time()
        hs = FileHandshake.FileHandshake()
        Print("\nTaking %s events. . ." % (self.NumEvts), SOFT)
        for evtNum in range(1, self.NumEvts+1):
            if (self.CheckTimeSinceLastReprogram(tProg)):
                tExtra += self.pauseForReprogram(hs,cmd)
                tProg = time.time()
            rcv = ETH.receive(20000)# rcv is string of Hex
            time.sleep(0.001)
            self.printStatusBar(evtNum)
            rcv = linkEth.hexToBin(rcv)
            f.write(rcv) # write received binary data into file
        self.EvtRate = float(evtNum)/(time.time()-t0-tExtra)
        Print("\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate), SOFT)

    def CollectASICtriggeredData(self):
        cmd = cmd_lib.CMD(self)
        f = self.OpenEthLinkAndDataFile()
        self.MainDataCollectionLoop(cmd,f)
        self.TurnOffTrigsAndHV_ClosePortsAndFiles(cmd,f)
        self.ConvertDataToRootFile()
        self.SaveDataCollectionParameters()

    def CollectRandomWindowData(self):
        cmd = cmd_lib.CMD(self)
        f = self.OpenEthLinkAndDataFile()
        self.RandomWindowDataCollectionLoop(cmd,f)
        self.TurnOffTrigsAndHV_ClosePortsAndFiles(cmd,f)
        self.ConvertDataToRootFile()

    def RandomWindowDataCollectionLoop(self,cmd,f):
        ETH.send(cmd.THoff())
        time.sleep(0.01)
        for ASIC in range(10):
            if ((2**ASIC & int(self.ASICmask,2)) > 0):
                if (self.DEBUG): Print("Sending run configuration to FPGA", SOFT)
                ETH.send(cmd.ASIC_HV_DAC_w_offset())
                time.sleep(0.01)
                self.RunConfig = cmd.Generate_Software_triggered_run_config_cmd(ASIC)
                ETH.send(self.RunConfig)
                time.sleep(0.01)
                t0 = time.time()
                Print("Taking %s events for ASIC %d . . ." % (self.NumEvts, ASIC), SOFT)
                for evtNum in range(1,self.NumEvts+1):
                    ETH.send(cmd.RandomWindow())
                    time.sleep(0.005)
                    ETH.send(cmd.forceTrig)
                    rcv = ETH.receive(20000)# rcv is string of Hex
                    time.sleep(0.005)
                    self.printStatusBar(evtNum)
                    rcv = linkEth.hexToBin(rcv)
                    f.write(rcv) # write received binary data into file
                self.EvtRate = float(evtNum)/(time.time()-t0)
                Print("\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate), SOFT)

    def SoftwareTriggeredDataCollectionLoop(self,cmd,f):
        ETH.send(cmd.HVoff())
        time.sleep(0.01)
        ETH.send(cmd.THoff())
        time.sleep(0.01)
        for ASIC in range(10):
            if ((2**ASIC & int(self.ASICmask,2)) > 0):
                if (self.DEBUG): Print("Sending run configuration to FPGA", SOFT)
                self.RunConfig = cmd.Generate_Software_triggered_run_config_cmd(ASIC)
                ETH.send(self.RunConfig)
                time.sleep(0.01)
                t0 = time.time()
                self.NumEvts = 128*self.NumSoftwareEvtsPerWin
                Print("Taking %s events for ASIC %d . . ." % (self.NumEvts, ASIC), SOFT)
                for evtNum in range(1,self.NumEvts+1):
                    ETH.send(cmd.Set_Readout_Window(((evtNum-1)*4)%512))
                    time.sleep(0.005)
                    ETH.send(cmd.forceTrig)
                    rcv = ETH.receive(20000)# rcv is string of Hex
                    time.sleep(0.005)
                    self.printStatusBar(evtNum)
                    rcv = linkEth.hexToBin(rcv)
                    f.write(rcv) # write received binary data into file
                self.EvtRate = float(evtNum)/(time.time()-t0)
                Print("\nOverall hit rate was %s%.2f Hz" % (OKGREEN,self.EvtRate), SOFT)

    def printStatusBar(self,evtNum):
        '''
        [---------------------------------------------------------------->] 100%
                                                                             '''
        status = evtNum/float(self.NumEvts)
        statusBar = BCYAN + "["
        for i  in range(int(72*status)):
            statusBar += "-"
        statusBar += ">"
        for i  in range(int(72*status),72):
            statusBar += " "
        statusBar += "] " + str(int(100*status)) + "%\033[m"
        sys.stdout.write('\r' + statusBar,)
        sys.stdout.flush()

    def pauseForReprogram(self,hs,cmd):
        Print("Pausing data collection\nRaising HV trim DACs", SOFT)
        Print("Closing port\nStarting handshake . . .", BCYAN)
        tProgStart = time.time()
        ETH.send(cmd.HVoff())
        time.sleep(0.1)
        ETH.close()
        hs.start_handshake()
        Print("Return-handshake acknowledged\nOpening port", BCYAN)
        ETH.open()
        time.sleep(0.2)
        Print("Sending run configuration to FPGA", SOFT)
        ETH.send(self.RunConfig)
        time.sleep(0.2)
        Print("Resuming data collection", SOFT)
        return(time.time()-tProgStart)

    def TurnOffTrigsAndHV_ClosePortsAndFiles(self,cmd,f):
        if (self.DEBUG): Print("Disabling ASIC triggering\nRaising HV trim DACs\nClosing port\nClosing data file", SOFT)
        f.close()
        ETH.send(cmd.turnOffASICtriggering)
        time.sleep(0.1)
        ETH.send(cmd.HVoff())
        time.sleep(0.2)
        ETH.close()
        time.sleep(0.1)

    def ConvertDataToRootFile(self, rootfile=""):
        if (rootfile==""):
            root_file = self.root_file
        else:
            root_file = rootfile
        if (self.ParserPedSubType == "-SWpeds"):
            self.ParserPedSubType += (" %s" % self.pedfile)
        Print("Parsing data . . .", SOFT)
        os.system("./bin/tx_ethparse1_ck temp/data.dat %s temp/triggerBits.txt %d %s" % (root_file,self.NumEvts,self.ParserPedSubType))
        os.system("echo -n > temp/data.dat") #clean binary file again to save disk space!
        Print("Data Parsed\nWaveform data saved in %s%s" % (OKBLUE,root_file), SOFT)

    def SaveDataCollectionParameters(self):
        Print(SOFT,"Saving data-collection parameters to %s%s\n\n" % (OKBLUE,self.root_file))
        for ASIC in range(10):
            if ((2**ASIC & int(self.HVmask,2)) > 0):
                ThDAC_Base    = np.asarray(self.Get_ASIC_Th_from_file(ASIC,'quiet'))
                ThDAC_offset  = np.asarray(self.ThDAC_offset)
                HVDAC         = np.asarray(self.Get_ASIC_HV_from_file(ASIC,'quiet')+self.HVDAC_offset)
                ROOT.WriteParametersToRootFile(self.root_file, self.rawHV, ThDAC_Base, ThDAC_offset, HVDAC, self.EvtRate, ASIC)

    def Plot_Peds_ManyASICs(self):
        ROOT.PlotPedestalStatisticsManyASICs("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistManyASICs.pdf")

    def Plot_Peds_OneASIC(self):
        ROOT.PlotPedestalStatisticsOneASIC("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistOneASIC.pdf")

    def Plot_Peds_Channel(self,ch):
        ROOT.PlotPedestalStatisticsOneChannel("temp/pedsTemp.root", "data/" + self.SN + "/plots/pedDistCh%d.pdf"%ch,ch)


    def ReadTrigFreq(self,ASIC):
        # (scalerCount is 32-bit value shared between 2 16-bit registers)
        T0 = self.ScalerCntNum16BitCycles*2**16/self.ClkFreq # count period in seconds
        scalerCount = ETH.readReg(138+ASIC) + ETH.readReg(168+ASIC)*65536
        freq = (scalerCount)/T0/1000 # freq in kHz
        return freq

    def ScanForThresholdBase(self,cmd,ASIC,ch):
        Print("\n*********** -Ch%d- ***********" % ch, OKBLUE)
        Print("Counting scalar frequencies at different thresholds (HV off).", SOFT)
        fmax = -1
        thBase = 4095
        for th in range (3700,3400,-1):
            ETH.send(cmd.Thr(ASIC,ch,th))
            time.sleep(0.01)#wait for counters to settle then read registers
            freq = self.ReadTrigFreq(ASIC)
            if freq > 0:
                Print("TrigDac=%3d %6.0f kHz" % (th,freq),SOFT)
            if (freq > fmax):
                fmax = freq
                thBase = th
        Print("Max Scalar Freq: %s%.1f" % (OKBLUE, fmax), SOFT)
        Print("Threshold Base: %s%d\n" % (OKBLUE, thBase), SOFT)
        time.sleep(1.0)
        return thBase

    def ScanForHVbase(self,cmd,ASIC,ch,thBase):
        Print("\nPerforming HV scan for channel %d" % ch, SOFT)
        fDiff = 10**6
        hvBase = 255
        ETH.send(cmd.Thr(ASIC,ch,thBase[ch]-self.HVscanTrigLevel))
        for hv in range (255,-1,-1): # 255 is lowest HV setting (i.e. most trim)
            ETH.send(cmd.HV(ASIC,ch,hv))
            time.sleep(0.01)#wait for counters to settle then read registers
            freq = self.ReadTrigFreq(ASIC)
            if freq > 0:
                Print("hvTrim=%3d %6.0f kHz" % (hv,freq),SOFT)
            if abs(freq-self.targetFreq) < fDiff:
                fDiff = abs(freq-self.targetFreq)
                hvBase = hv
        Print("Found starting HV value: %s%d\n" % (OKBLUE,hvBase), SOFT)
        time.sleep(1.0)
        return hvBase

    def WriteHVandThBaseValuesToFile(self,ASIC,thBase,HVbase):
        calib_file = "data/%s/calib/HVandTH/%s_HV%s_ASIC%d.txt" % (self.SN, self.SN, self.strHV, ASIC)
        if not (os.path.isdir("data/%s/calib/HVandTH" % self.SN)): # create path if it does not exist
            if (self.DEBUG): Print("\nmaking directory data/%s/calib/HVandTH" % self.SN, OKBLUE)
            os.system("mkdir -p data/%s/calib/HVandTH" % self.SN) # make deepest subdir with parents
        outfile = open(calib_file, 'w')
        for i in range(15):
            outfile.write("%d\t%d\n" % (thBase[i], HVbase[i]))
        outfile.close()
        Print("Writing calibration values in %s%s" % (OKBLUE,calib_file), SOFT)

    def SendCountScalersConfig(self, ETH):
        #ETH.send(ETH.syncwd + 'AF4D0B00'+'AE000100'+'AF4DCB00'+'AE000100') # for KLM SciFi -- don't know why it's here
        #time.sleep(0.1)
        #ETH.send(ETH.syncwd + 'AF2F0004'+'AF300004'+'AE000100')# 0000 0000 0000 0100 --> (47) TRIG_SCALER_CLK_MAX, (48) TRIG_SCALER_CLK_MAX_TRIGDEC
        #time.sleep(0.1)
        ETH.send(ETH.syncwd + 'AF4A0136'+'AE000100')# 0011 0110 (7 downto 0) WAVE_TRIGASIC_DUMP_CFG, 0001 (11 downto 8) PEDSUB_DATAOUT_MODE
        time.sleep(0.1)
        ETH.send(ETH.syncwd + 'AF2F0004'+'AE000100')
        time.sleep(0.1)

    def MeasureTrigDAC_and_HV_DAC_BaseValues(self):
        cmd = cmd_lib.CMD(self)
        for ASIC in range(10):
            if ((2**ASIC & int(self.ASICmask,2)) > 0):
                thBase   = [3200 for i in range(15)]
                HVbase   = [255  for i in range(15)]
                ETH.open()
                #self.SendCountScalersConfig(ETH)
                #ETH.send(cmd.CountScalersConfig())
                ETH.send(ETH.syncwd + 'AF4A0136'+'AE000100')
                time.sleep(0.1)
                ETH.send(cmd.Reg47_NumClkCyclesForTrigScalerCounter(self.ScalerCntNum16BitCycles))
                time.sleep(0.1)
                for ch in range(15):
                    if ((2**ch & int(self.HVmask,2)) > 0):
                        ETH.send(cmd.HVoff())
                        time.sleep(0.1)
                        ETH.send(cmd.THoff())
                        time.sleep(0.1)
                        thBase[ch] = self.ScanForThresholdBase(cmd,ASIC,ch)
                        time.sleep(0.01)
                        HVbase[ch] = self.ScanForHVbase(cmd,ASIC,ch,thBase)
                        ETH.send(cmd.HVoff())
                        time.sleep(0.01)
                        ETH.send(cmd.THoff())
                        time.sleep(0.1)
                ETH.close()
                self.WriteHVandThBaseValuesToFile(ASIC,thBase,HVbase)
                self.PrintThList(thBase)
                self.PrintHVList(HVbase)

    def MeasurePedestalDistribution(self,opt=1):
        cmd = cmd_lib.CMD(self)
        self.NumSoftwareEvtsPerWin = opt
        f = self.OpenEthLinkAndDataFile()
        self.SoftwareTriggeredDataCollectionLoop(cmd,f)
        self.TurnOffTrigsAndHV_ClosePortsAndFiles(cmd,f)
        self.ConvertDataToRootFile("temp/pedsTemp.root")

    def CreatePedestalMasterFile(self,opt=128):
        cmd = cmd_lib.CMD(self)
        self.MeasurePedestalDistribution(cmd,opt)
        ROOT.AveragePedestalTTree(self.pedfile,int(self.ASICmask,2),float(self.NumSoftwareEvtsPerWin))
        Print("Averaged pedestal data saved in %s%s" % (OKBLUE,self.pedfile), SOFT)
        os.system("chmod g+w %s" % self.pedfile)
