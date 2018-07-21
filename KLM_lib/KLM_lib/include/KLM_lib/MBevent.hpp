#ifndef MBevent_h
#define MBevent_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>
#include "TTree.h"
#include "TH2.h"
#include "TGraph.h"
#include <memory>
#include "KLM_lib/Platform.hh"

class TTree;

ROOTCLASS MBevent {
public :
#ifndef __CINT__
  std::shared_ptr<TTree>          fChain;
#endif
  // Declaration of leaf types

  Int_t           EvtNum;
  Int_t           AddNum;
  Int_t           WrAddNum;
  Int_t           Wctime;
  Int_t           ASIC;
  Int_t           ADC_counts[16][128];
  Int_t           PeakTime[16];
  Int_t           PeakVal[16];

  MBevent(const std::string& treeName="tree");
  inline ~MBevent(){
    fChain->Write();
  }
  void Fill();



};

#endif
