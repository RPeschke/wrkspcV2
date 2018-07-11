void PlotSomeWaveforms(const char* root_file, const char* SN) {
  gROOT->Reset();
  gStyle->SetOptStat(0);
  // declare tree variables
  Int_t EvtNum, AddNum,  WrAddNum, Wctime, ASIC;
  Float_t Time[16];
  Int_t PeakVal[16], Sample[16][128];



  TFile* file = new TFile(root_file,"READ");
  TTree* tree = (TTree*)file->Get("tree");
  TCanvas* canvas1 = new TCanvas("waveforms", "Waveforms", 1100, 850);
  canvas1->Divide(4, 4); // make 4 pads per canvas

  // declare memory for 4 histograms & configure
  TH2F* h1[16];
  for (int i=0; i<16; i++){
    h1[i] = new TH2F("", "", 128,0,128, 1200,-600,600);
    h1[i]->GetYaxis()->SetTitleOffset(1.5);
    h1[i]->GetYaxis()->SetTitle("ADC Counts");
  }

  char xlabel[50];
  char m_coord[12];
  char wlabel[20];
  int pad, plotNo = 0, yTH=0;

  tree->SetBranchAddress("ADC_counts", Sample);
  tree->SetBranchAddress("AddNum", &AddNum);
  tree->SetBranchAddress("PeakVal", PeakVal);
  tree->SetBranchAddress("Time", Time);

  int numEnt = tree->GetEntriesFast();
  int numPlots = 16;//100;//numEnt;
  for(int e=0; e<1; e++) {
    tree->GetEntry(e);

    //if (Time[argCH]<96 && Time[argCH]>10){
    for(int c=0; c<16; c++){
      sprintf(wlabel, "Windows %d-%d", AddNum, (AddNum+3)%512);
      h1[c]->SetTitle(wlabel);
      h1[c]->Reset();
      sprintf(xlabel, "Ch_%d Sample No.", c);
      h1[c]->GetXaxis()->SetTitle(xlabel);

      //// label peak value on plot
      //Double_t xpeak = (Double_t) Time[argCH];
      //Double_t ypeak = (Double_t) PeakVal[argCH];
      TMarker *m = new TMarker(Time[c],0, 22);
      yTH = (Time[c]>0) ? 100:0 ;
      m->SetY(yTH);
      //TMarker *m = new TMarker(Time[argCH], PeakVal[argCH], 22);
      m->SetMarkerColorAlpha(kBlue, 0.35);
      m->SetMarkerStyle(kPlus);
      m->SetMarkerSize(5);
      //h1[c]->GetListOfFunctions()->Add(m);

      //// print coordinates on plot
      //sprintf(m_coord, "[%3.0f, %3.0f]", xpeak, ypeak);
      //TPaveLabel *l = new TPaveLabel(xpeak+3,ypeak+25,xpeak+23,ypeak+75, m_coord);
      //h1[c]->GetListOfFunctions()->Add(l);

      for(int j=0; j<128; j++) { // sample No.
        Double_t x = (Double_t) j;
        Double_t y = (Double_t) Sample[c][j];
        h1[c]->Fill(x, y);
      }
      canvas1->cd(c+1);
      h1[c]->Draw();


    }
  }

  canvas1->Update();
  char plotTitle[50];
  sprintf(plotTitle, "data/%s/plots/SomeMultiChannelWaveforms.pdf", SN);
  canvas1->Print(plotTitle);
  canvas1->Update();

  // free up memory declared as "new"
  //delete canvas1;
  //for (int i=0; i<4; i++){delete h1[i];}
}// note: file closes upon exiting function!
