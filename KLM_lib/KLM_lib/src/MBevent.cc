#include "KLM_lib/MBevent.hpp"

MBevent::MBevent(const std::string& treeName){
  fChain = std::make_shared<TTree>(treeName.c_str(), treeName.c_str());
  fChain->Branch("EvtNum", &EvtNum, "EvtNum/I");
  fChain->Branch("AddNum", &AddNum, "AddNum/I");
  fChain->Branch("WrAddNum", &WrAddNum, "WrAddNum/I");
  fChain->Branch("Wctime", &Wctime, "Wctime/I");
  fChain->Branch("ASIC", &ASIC, "ASIC/I");
  fChain->Branch("ADC_counts", ADC_counts, "ADC_counts[16][128]/I");
  fChain->Branch("PeakTime", PeakTime, "PeakTime[16]/I");
  fChain->Branch("PeakVal", PeakVal, "PeakVal[16]/I");
}


void   MBevent::Fill(){
  fChain->Fill();
}
