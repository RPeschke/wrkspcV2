void PlotPedestalStatisticsManyASICs(const char* root_file, const char* out_pdf) {
  gROOT->Reset();
  // declare tree variables
  Int_t EvtNum, AddNum,  WrAddNum, ASIC, Sample[16][128];
//  Int_t Wctime, ASIC, PeakTime[16];



  TFile* file = new TFile(root_file,"READ");
  TTree* tree = (TTree*)file->Get("tree");
  TCanvas* canv = new TCanvas("pedestals", "Pedestals", 1100, 850);
  canv->Divide(5,2); // make 10 pads per canvas

  tree->SetBranchAddress("AddNum", &AddNum);
  tree->SetBranchAddress("ASIC", &ASIC);
  tree->SetBranchAddress("ADC_counts", Sample);
  tree->GetEntry(0);

  char plotTitle[100];
  TH2I* hPeds[10];
  for (int asic = 0; asic < 10; asic++) {
    sprintf(plotTitle, "ASIC %d, Ped. Compensated Baseline, All Samp/Ch Except Calib Ch", asic);
    hPeds[asic] = new TH2I("", plotTitle, 101,-50,50, 512,0,512);
    hPeds[asic]->GetXaxis()->SetTitle("Wilk. ADC Counts");
    hPeds[asic]->GetYaxis()->SetTitle("Window #");
  }

  int NumEnt = tree->GetEntriesFast();
  for (int e=0; e<NumEnt; e++){
    tree->GetEntry(e);
    for (int ch=0; ch<15; ch++){
      for (int grp=0; grp<4; grp++){
        for (int samp=0; samp<32; samp++){
          hPeds[ASIC]->Fill(Sample[ch][samp+32*grp], AddNum+grp);
        }
      }
    }
  }
  //canv->cd(1);
  for (int asic = 0; asic < 10; asic++) {
    canv->cd(asic+1);
    hPeds[asic]->Draw("COLZ");
  }
  canv->Update();
  gSystem->Sleep(10);
  canv->Print(out_pdf);
}

void PlotPedestalStatisticsOneASIC(const char* root_file, const char* out_pdf) {
  gROOT->Reset();
  // declare tree variables
  Int_t EvtNum, AddNum,  WrAddNum, ASIC, Sample[16][128];
//  Int_t Wctime, ASIC, PeakTime[16];



  TFile* file = new TFile(root_file,"READ");
  TTree* tree = (TTree*)file->Get("tree");
  TCanvas* canv = new TCanvas("pedestals", "Pedestals", 1100, 850);
  canv->Divide(4,4); // make 10 pads per canvas

  tree->SetBranchAddress("AddNum", &AddNum);
  tree->SetBranchAddress("ASIC", &ASIC);
  tree->SetBranchAddress("ADC_counts", Sample);
  tree->GetEntry(0);

  char plotTitle[100];
  TH2I* hPeds[16];
  for (int chNo = 0; chNo < 16; chNo++) {
    sprintf(plotTitle, "Ch %d, Ped. Compensated Baseline", chNo);
    hPeds[chNo] = new TH2I("", plotTitle, 101,-50,50, 512,0,512);
    hPeds[chNo]->GetXaxis()->SetTitle("Wilk. ADC Counts");
    hPeds[chNo]->GetYaxis()->SetTitle("Window #");
  }

  int NumEnt = tree->GetEntriesFast();
  for (int e=0; e<NumEnt; e++){
    tree->GetEntry(e);
    for (int ch=0; ch<15; ch++){
      for (int grp=0; grp<4; grp++){
        for (int samp=0; samp<32; samp++){
          hPeds[ch]->Fill(Sample[ch][samp+32*grp], AddNum+grp);
        }
      }
    }
  }
  //canv->cd(1);
  for (int chNo = 0; chNo < 16; chNo++) {
    canv->cd(chNo+1);
    hPeds[chNo]->Draw("COLZ");
  }
  canv->Update();
  gSystem->Sleep(10);
  canv->Print(out_pdf);
}
