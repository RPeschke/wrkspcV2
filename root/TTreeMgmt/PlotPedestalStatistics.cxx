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
    hPeds[asic] = new TH2I("", plotTitle, 50,-25,25, 512,0,512);
    hPeds[asic]->GetXaxis()->SetTitle("Wilk. ADC Counts");
    hPeds[asic]->GetYaxis()->SetTitle("Window #");
  }

  int NumEnt = tree->GetEntriesFast();
  for (int e=0; e<NumEnt; e++){
    tree->GetEntry(e);
    for (int ch=0; ch<15; ch++){
      for (int win=0; win<4; win++){
        for (int samp=0; samp<32; samp++){
          hPeds[ASIC]->Fill(Sample[ch][samp+32*win], AddNum+win);
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
  gStyle->SetOptStat(0);
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
//    hPeds[chNo] = new TH2I("", plotTitle, 400,2200,2600, 512,0,512);
    hPeds[chNo] = new TH2I("", plotTitle, 50,-25,25, 512,0,512);
//    hPeds[chNo] = new TH2I("", plotTitle, 4000,-200,3800, 512,0,512);
//    hPeds[chNo] = new TH2I("", plotTitle, 100,-50,50, 512,0,512);
    hPeds[chNo]->GetXaxis()->SetTitle("Wilk. ADC Counts");
    hPeds[chNo]->GetYaxis()->SetTitle("Window #");
  }

  int NumEnt = tree->GetEntriesFast();
  for (int e=0; e<NumEnt; e++){
    tree->GetEntry(e);
    for (int ch=0; ch<15; ch++){
      for (int win=0; win<4; win++){
        for (int samp=0; samp<32; samp++){
          hPeds[ch]->Fill(Sample[ch][samp+32*win], AddNum+win);
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




//void PlotPedestalStatisticsAllCellsOneASIC(const char* root_file, const char* out_pdf) {
//  gStyle->SetOptStat(0);
//  //gROOT->Reset();
//  // declare tree variables
//  Int_t EvtNum, AddNum,  WrAddNum, ASIC, Sample[16][128];
////  Int_t Wctime, ASIC, PeakTime[16];
//
//  TFile* file = new TFile(root_file,"READ");
//  TTree* tree = (TTree*)file->Get("tree");
//  TCanvas* canv = new TCanvas("pedestals", "Pedestals", 1100, 850);
//  TPad* pad[512];
//
//  tree->SetBranchAddress("AddNum", &AddNum);
//  tree->SetBranchAddress("ASIC", &ASIC);
//  tree->SetBranchAddress("ADC_counts", Sample);
//  tree->GetEntry(0);
//
//  char plotTitle[100];
//  char padName[20]; float xi, xf, yi, yf;
//  TH2I* hPeds[512];
//  for (int ch = 0; ch < 16; ch++) {
//    xi = ch*.0625; xf = (1+ch)*.0625;
//    for (int sa = 0; sa < 32; sa++) {
//      //sprintf(plotTitle, "Ch %d, Ped. Compensated Baseline", ch);
//      hPeds[ch*32+sa] = new TH2I("", plotTitle, 50,-25,25, 512,0,512);
//      sprintf(padName,"ch%dsa%d",ch,sa);
//      yi = sa*.03125; yf = (1+sa)*.03125;
//      pad[ch*32+sa] = new TPad(padName,"",xi,yi,xf,yf);
//      pad[ch*32+sa]->Draw();
//    }
//  }
//
//  int NumEnt = tree->GetEntriesFast();
//  for (int e=0; e<NumEnt; e++){
//    tree->GetEntry(e);
//    for (int ch=0; ch<15; ch++){
//      for (int win=0; win<4; win++){
//        for (int samp=0; samp<32; samp++){
//          hPeds[ch*32+samp]->Fill(Sample[ch][samp+32*win], AddNum+win);
//        }
//      }
//    }
//  }
//  for (int ch=0; ch<16; ch++) {
//    for (int sa=0; sa<32; sa++) {
//      pad[ch*32+sa]->cd();
//      hPeds[ch*32+sa]->Draw("COLZ");
//    }
//  }
//  canv->Update();
//  gSystem->Sleep(10);
//  canv->Print(out_pdf);
//}


void PlotPedestalStatisticsOneChannel(const char* root_file, const char* out_pdf, const int argCH) {
  //gROOT->Reset();
  gStyle->SetOptStat(0);
  // declare tree variables
  Int_t EvtNum, AddNum,  WrAddNum, ASIC, Sample[16][128];
//  Int_t Wctime, ASIC, PeakTime[16];

  TFile* file = new TFile(root_file,"READ");
  TTree* tree = (TTree*)file->Get("tree");
  tree->SetBranchAddress("AddNum", &AddNum);
  tree->SetBranchAddress("ASIC", &ASIC);
  tree->SetBranchAddress("ADC_counts", Sample);
  tree->GetEntry(0);

  char plotTitle[100];
  TH2I* hPeds[32];
  for (int sa = 0; sa < 32; sa++) {
    sprintf(plotTitle, "Sa %d Ped. Distribution", sa);
    hPeds[sa] = new TH2I("", plotTitle, 50,-25,25, 512,0,512);
  }

  TCanvas* canv = new TCanvas("pedestals", "Pedestals", 1100, 850);
  TPad* pad[32];
  float xi, xf, yi, yf; int samp; char padName[20];
  for (int npy = 0; npy < 4; npy++) {
    yi = 1.0-(npy+1)/4.0; yf = 1.0-(npy)/4.0;
    for (int npx = 0; npx < 8; npx++) {
      xi = (npx)/8.0; xf = (npx+1)/8.0;
      samp=npy*8+npx;
      sprintf(padName,"sa%d",samp);
      pad[samp] = new TPad("",padName,xi,yi,xf,yf);
      pad[samp]->Draw();
    }
  }

  int NumEnt = tree->GetEntriesFast();
  for (int e=0; e<NumEnt; e++){
  tree->GetEntry(e);
    for (int win=0; win<4; win++){
      for (int samp=0; samp<32; samp++){
        hPeds[samp]->Fill(Sample[argCH][samp+32*win], AddNum+win);
      }
    }
  }
  for (int sa=0; sa<32; sa++) {
    pad[sa]->cd();
    hPeds[sa]->Draw("COLZ");
  }
  canv->Update();
  gSystem->Sleep(10);
  canv->Print(out_pdf);
}
