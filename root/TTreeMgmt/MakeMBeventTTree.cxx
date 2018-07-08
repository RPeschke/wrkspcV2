#include "Riostream.h"

void WriteParametersToRootFile(
  const char* root_file,
  const float rawHV,
  const int* thBase,
  const int* thOffset,
  const int* HV_DAC,
  const float hitRate
)
{

  TFile* file = new TFile(root_file, "RECREATE");
  TTree* tree = new TTree("parameters","Data collection parameters");

  tree->Branch("RawHV", &rawHV, "RawHV_V/F");
  tree->Branch("ThBase", thBase, "ThresholdBase[16]/I");
  tree->Branch("ThOffset", thOffset, "ThresholdOffset[16]/I");
  tree->Branch("HV_DAC", HV_DAC, "HV_DAC[16]/I");
  tree->Branch("TrigRate", &trigRate, "TrigRate_Hz/F");

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
    infile >>      EvtNum      ;
    infile >>      AddNum      ;
    infile >>      WrAddNum    ;
    infile >>      Wctime      ;
    infile >>      ASIC        ;
    for (int i=0; i<16; i++) {
      offset = (i==15) ? 2048 : 3400;
      infile >>  peakTime ; // FW feature extraction
      infile >>  peakVal ; // FW feature extraction
      for (int j=0; j<128 j++) {
          infile >> tempSamp;               // remaining samples
          Sample[i][j]=offset-tempSamp;
      }// END SAMP LOOP
    }// END CH LOOP
    tree->Fill();
    if (!infile.good()) break;
    nlines++;
  }// END EVENT LOOP
  printf("Read %d lines.\n",nlines);
  infile.close();
  file->Write("tree");
  file->Close();
  delete file;
}
