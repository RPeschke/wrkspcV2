#!/usr/bin/env python
import sys, time, os, csv, random, run_lib

SOFT       =  "\033[95m"
OKBLUE     =  "\033[94m"
OKGREEN    =  "\033[92m"
FATAL      =  "\033[1;91m"
BCYAN      =  "\033[1;96m"
def Print(s,c):
    print"%s%s\033[m"%(c,str(s))

class CMD:#class used to generate UDP packets for sending over ethernet
    def __init__(self, run):
        self.run = run
        self.syncwd = "000000010253594e4300000000"
        self.forceTrig = self.syncwd + "AF00FFFF"+"AF00FFFF"+"AF370001"+"AE000001"+"AF370000"+"AE000001"+"AF320001"+"AE000001"+"AF320000" # modified original from AF00FFF+AF00FFFFF / CK
        self.turnOffASICtriggering = self.syncwd + "AF270000" + "AE000100"

    def HVoff(self):
        cmd = self.syncwd
        for ASIC in range(10):
            if ((2**ASIC & int(self.run.ASICmask,2)) > 0):
                for ch in range(15):
                    cmd += hex( int('C',16)*(2**28) | ASIC*(2**20) | (ch)*(2**16) | 255 ).split('x')[1] +"AE000100"
        return cmd

    def ASIC_HV_DAC_w_offset(self):
        cmd = self.syncwd
        for ASIC in range(10):
            if ((2**ASIC & int(self.run.ASICmask,2)) > 0):
                HVDAC_base = self.run.Get_ASIC_HV_from_file(ASIC)
                for ch in range(len(HVDAC_base)):
                    if (2**ch & int(self.run.HVmask,2)):
                        cmd += hex( int('C',16)*(2**28) | ASIC*(2**20) | (ch)*(2**16) | HVDAC_base[ch]+self.run.HVDAC_offset[ch] ).split('x')[1] +"AE000100"
                    else:
                        cmd += hex( int('C',16)*(2**28) | ASIC*(2**20) | (ch)*(2**16) | 255).split('x')[1] +"AE000100"
        return cmd

    def THoff(self):
        cmd = self.syncwd
        for ASIC in range(10):
            if ((2**ASIC & int(self.run.ASICmask,2)) > 0):
                for ch in range(15):
                    cmd += hex( int('B',16)*(2**28) | ASIC*(2**24) | (2*ch)*(2**16) | 4095 ).split('x')[1] +"AE000100"
        return cmd

    def Thr(self,ASIC,ch,th):
        cmd = self.syncwd
        cmd += hex( int('B',16)*(2**28) | ASIC*(2**24) | (2*ch)*(2**16) | th ).split('x')[1]
        return cmd

    def HV(self,ASIC,ch,hv):
        cmd = self.syncwd
        cmd += hex( int('C',16)*(2**28) | ASIC*(2**20) | (ch)*(2**16) | hv ).split('x')[1]
        return cmd

    def ASIC_Th_DAC_w_offset(self):
        cmd = self.syncwd
        for ASIC in range(10):
            if ((2**ASIC & int(self.run.ASICmask,2)) > 0):
                ThDAC_base = self.run.Get_ASIC_Th_from_file(ASIC)
                for ch in range(len(ThDAC_base)):
                    if (2**ch & int(self.run.TrigMask,2)):
                        cmd += hex( int('B',16)*(2**28) | ASIC*(2**24) | (2*ch)*(2**16) | ThDAC_base[ch]+self.run.ThDAC_offset[ch] ).split('x')[1] +"AE000100"
                    else:
                        cmd += hex( int('B',16)*(2**28) | ASIC*(2**24) | (2*ch)*(2**16) | 4095 ).split('x')[1] +"AE000100"
        return cmd

    def Generate_ASIC_triggered_run_config_cmd(self):
        cmd = self.syncwd
        cmd += self.ASIC_HV_DAC_w_offset().replace(self.syncwd,'')
        cmd += self.ASIC_Th_DAC_w_offset().replace(self.syncwd,'')
        cmd += "AF250000" + "AE000100" # disable ext. trig
        cmd += "AF3E0000" + "AE000100" # win start set to zero for internal triggering
        cmd += hex(int('AF360000',16) | 0                             | self.run.ASIClookbackParam  ).split('x')[1] +"AE000100"#set win offset
        cmd += hex(int('AF330000',16) | 0                             | int(self.run.ASICmask,2)    ).split('x')[1] +"AE000100"#set asic number
        cmd += hex(int('AF260000',16) | self.run.FWpedSubType*(2**12) | 2**7                        ).split('x')[1] +"AE000100"#CMDREG_PedDemuxFifoOutputSelect(13 downto 12)-->either wavfifo or pedfifo,CMDREG_PedSubCalcMode(10 downto 7)-->currently only using bit 7: 1 for peaks 2 for troughs, sample offset is 3400 o6 600 respectively
        cmd += hex(int('AF270000',16) | 1*(2**15)                     | int(self.run.ASICmask,2)    ).split('x')[1] +"AE000100"#set trig mode & asic trig enable
        cmd += hex(int('AF4A0000',16) | self.run.FWoutMode*(2**8)     | 1*2**4 + 2*2**0             ).split('x')[1] +"AE000100"#set outmode and win boundaries for trigger bits: x12 scans 1 win back and two forward
        cmd += "AF4F0002" # external trigger bit format
        return cmd

    def Generate_Software_triggered_run_config_cmd(self,ASIC):
        cmd  = self.syncwd
        cmd += hex(int('AF330000',16) | 2**ASIC           ).split('x')[1] +"AE000100" # set asic number
        cmd += "AF3E8000"+"AE000100" # set win start
        cmd += "AF250000"+"AE000100" # disable ext. trig
        cmd += hex(int('AF270000',16) | 2**ASIC           ).split('x')[1] +"AE000100" # set trig mode & asic trig enable
        cmd += "AF360000" +"AE000100" # set ASIC lookback parameter to zero
        cmd += hex(int('AF260000',16) | self.run.FWpedSubType*(2**12)      ).split('x')[1] +"AE000100" # CMDREG_PedDemuxFifoOutputSelect(13 downto 12)-->either wavfifo or pedfifo,CMDREG_PedSubCalcMode(10 downto 7)-->currently only using bit 7: 1 for peaks 2 for troughs, sample offset is 3400 o6 600 respectively
        cmd += hex(int('AF4A0000',16) | self.run.FWoutMode*(2**8)     | 18 ).split('x')[1] +"AE000100" # set outmode and win boundaries for trigger bits: x12 scans 1 win back and two forward
        cmd += "AF4F0000" # external trigger bit format
        return cmd

    def Set_Readout_Window(self, win):
        if (win<0 | win>511):
            Print("Invalid window number: (%d)" % win, FATAL)
            Print("Exiting . . .", FATAL)
            exit(-1)
        cmd = self.syncwd + hex(int('AF3E8000',16) | win).split('x')[1]
        return cmd

    def RandomWindow(self):
        cmd = self.syncwd
        cmd += self.Set_Readout_Window(random.randint(0,511))
        return cmd

    #def CountScalersConfig(self):
    #    cmd = self.syncwd
    #    cmd += 'AF4D0B00'+'AE000100'+'AF4DCB00'+'AE004000' # for KLM SciFi -- don't know why it's here
    #    cmd += 'AF2F0004'+'AF300004'+'AE004000'# 0000 0000 0000 0100 --> (47) TRIG_SCALER_CLK_MAX, (48) TRIG_SCALER_CLK_MAX_TRIGDEC
    #    cmd += 'AF4A0136'+'AE004000'# 0011 0110 (7 downto 0) WAVE_TRIGASIC_DUMP_CFG, 0001 (11 downto 8) PEDSUB_DATAOUT_MODE
    #    return cmd

    def Reg47_NumClkCyclesForTrigScalerCounter(self,NumClkCycles=4):
        return self.syncwd + hex(int('AF2F0000',16) | NumClkCycles).split('x')[1] +"AE000100"
