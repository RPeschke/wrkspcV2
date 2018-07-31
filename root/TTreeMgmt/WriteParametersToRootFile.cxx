#include "Riostream.h"

void WriteParametersToRootFile(
  const char* root_file,
  const float rawHV,
  const long int thDAC_Base[15],
  const long int thDAC[15],
  const long int HV_DAC[15],
  const float trigRate,
  const int ASIC
)
{

  Float_t RawHV    = rawHV;
  Float_t TrigRate = trigRate;
  Int_t   asic     = ASIC;
  Int_t   ThDAC_Base[15], ThDAC[15], HVtrimDAC[15];

  for (int ch=0; ch<15; ch++) {
    ThDAC_Base[ch] = (int)thDAC_Base[ch];
    ThDAC[ch]      = (int)thDAC[ch];
    HVtrimDAC[ch]  = (int)HV_DAC[ch];
  }

  TFile* file = new TFile(root_file, "UPDATE");
  TTree* tree = new TTree("parameters","Data collection parameters");

  tree->Branch("ASIC", &asic, "ASIC_V/I");
  tree->Branch("RawHV", &RawHV, "RawHV_V/F");
  tree->Branch("ThDAC_Base", ThDAC_Base, "ThresholdBaseValue_12bitDACvalue[15]/I");
  tree->Branch("ThDAC", ThDAC, "ThresholdSetting_12bitDACvalue[15]/I");
  tree->Branch("HVtrimDAC", HVtrimDAC, "HV_Trim_8bit5V_DACvalue[15]/I");
  tree->Branch("TrigRate", &TrigRate, "TrigRate_Hz/F");

  tree->Fill();
  file->Write("parameters");
  file->Close();
}
