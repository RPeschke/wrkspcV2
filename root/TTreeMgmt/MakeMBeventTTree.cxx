#include "Riostream.h"

void WriteParametersToRootFile(
  const char* root_file,
  const float rawHV,
  const long int thDAC_Base[15],
  const long int thDAC[15],
  const long int HV_DAC[15],
  const float trigRate
)
{

  Float_t RawHV    = rawHV;
  Float_t TrigRate = trigRate;
  Int_t   ThDAC_Base[15], ThDAC[15], HVtrimDAC[15];

  for (int ch=0; ch<15; ch++) {
    ThDAC_Base[ch] = (int)thDAC_Base[ch];
    ThDAC[ch]      = (int)thDAC[ch];
    HVtrimDAC[ch]  = (int)HV_DAC[ch];
  }

  TFile* file = new TFile(root_file, "RECREATE");
  TTree* tree = new TTree("parameters","Data collection parameters");

  tree->Branch("RawHV", &RawHV, "RawHV_V/F");
  tree->Branch("ThDAC_Base", ThDAC_Base, "ThresholdBaseValue_12bitDACvalue[15]/I");
  tree->Branch("ThDAC", ThDAC, "ThresholdSetting_12bitDACvalue[15]/I");
  tree->Branch("HVtrimDAC", HVtrimDAC, "HV_Trim_8bit5V_DACvalue[15]/I");
  tree->Branch("TrigRate", &TrigRate, "TrigRate_Hz/F");

  tree->Fill();
  file->Write("parameters");
  file->Close();
}

void MakeMBeventTTree(const char* ascii_input, const char* root_output) {
  std::ifstream infile;
  infile.open(ascii_input);


  // TTree Variables
  Int_t   EvtNum, AddNum,  WrAddNum, Wctime, ASIC, peakTime, peakVal, Sample[16][128]; // raw data variables

  TFile* file = new TFile(root_output, "UPDATE");
  TTree* tree = new TTree("tree","SciFi tracker output via KLM motherboard");

  tree->Branch("EvtNum", &EvtNum, "EvtNum/I");
  tree->Branch("AddNum", &AddNum, "AddNum/I");
  tree->Branch("WrAddNum", &WrAddNum, "WrAddNum/I");
  tree->Branch("Wctime", &Wctime, "Wctime/I");
  tree->Branch("ASIC", &ASIC, "ASIC/I");
  tree->Branch("PeakTime", &peakTime, "PeakTime/I");
  tree->Branch("PeakVal", &peakVal, "PeakVal/I");
  tree->Branch("ADC_counts", Sample, "ADC_counts[16][128]/I");

  int nlines = 0, tempSamp = 0, offset = 0;
  while (1) { // loops intil break is reached
    if (!infile.good()) break;
    infile >>      EvtNum      ;
    infile >>      AddNum      ;
    infile >>      WrAddNum    ;
    infile >>      Wctime      ;
    infile >>      ASIC        ;
    for (int i=0; i<16; i++) {
      offset = (i==15) ? 2048 : 3400;
      infile >>  peakTime ; // FW feature extraction
      infile >>  peakVal ; // FW feature extraction
      for (int j=0; j<128; j++) {
          infile >> tempSamp;               // remaining samples
          Sample[i][j]=offset-tempSamp;
      }// END SAMP LOOP
    }// END CH LOOP
    tree->Fill();
    nlines++;
  }// END EVENT LOOP
  printf("Read %d lines.\n",nlines);
  infile.close();
  file->Write("tree");
  file->Close();
  delete file;
}
