void AveragePedestalTTree(const char* root_file, const int ASICmask, const float NoAvgs) {
  //gROOT->Reset();
  Int_t AddNum, ASIC, ADC_counts[16][128];
  Int_t outASIC, PedSample[10][16][512][32], OutPedSample[16][512][32];
  for(int i=0;i<16;i++){
    for(int j=0;j<512;j++){
      for(int k=0;k<32;k++){
        OutPedSample[i][j][k]=0;
        for(int n=0;n<10;n++)PedSample[n][i][j][k]=0;
      }
    }
  }

  TFile* infile = new TFile("temp/pedsTemp.root","READ");
  TTree* intree = (TTree*)infile->Get("tree");
  intree->SetBranchAddress("ADC_counts", ADC_counts);
  intree->SetBranchAddress("ASIC", &ASIC);
  intree->SetBranchAddress("AddNum", &AddNum);

  for (int e=0; e<intree->GetEntriesFast(); e++) {
    intree->GetEntry(e);
    for (int i=0;  i<16; i++) {
      for (int j=0; j<4; j++) {
        for (int k=0; k<32 ; k++) {
          PedSample[ASIC][i][(AddNum+j)%512][k] += ADC_counts[i][j*32+k];
        }
      }
    }
  }
  infile->Close();

  TFile* outfile = new TFile(root_file,"RECREATE");
  TTree* outtree = new TTree("pedTree", "TargetX Pedestal Data (ASIC# = Entry#)");
  outtree->Branch("ADC_counts", OutPedSample, "ADC_counts[16][512][32]/I");
  outtree->Branch("ASIC", &outASIC, "ASIC/I");
  for (int n=0; n<10; n++) {
    if ((int)TMath::Power(2,n) & ASICmask){
      outASIC = n;
      for (int i=0;  i<16; i++) {
        for (int j=0; j<512; j++) {
          for (int k=0; k<32 ; k++) {
            OutPedSample[i][j][k] = (int)((float)PedSample[n][i][j][k]/(float)NoAvgs);
          }
        }
      }
    }
    else {
      outASIC = -1;
      for (int i=0;  i<16; i++) {
        for (int j=0; j<512; j++) {
          for (int k=0; k<32 ; k++) {
            OutPedSample[i][j][k] = 0;
          }
        }
      }
    }
    outtree->Fill();
  }
  outtree->Write();
  outfile->Close();
}
