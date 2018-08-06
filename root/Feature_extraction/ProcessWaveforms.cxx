#include "Riostream.h"
#include "TMath.h"


void ProcessWaveformData(const char* root_input) {

  TFile* file = new TFile(root_input, "UPDATE");
  TTree* tree = (TTree*)file->Get("tree");


  // TTree Variables
  Int_t   EvtNum, AddNum,  WrAddNum, Wctime, ASIC, tFW, qFW, Sample[16][128];
  tree->SetBranchAddress("EvtNum", &EvtNum);
  tree->SetBranchAddress("AddNum", &AddNum);
  tree->SetBranchAddress("WrAddNum", &WrAddNum);
  tree->SetBranchAddress("Wctime", &Wctime);
  tree->SetBranchAddress("ASIC", &ASIC);
  tree->SetBranchAddress("ADC_counts", Sample);

  //TFile* OutFile = new TFile(root_output, "RECREATE");
  TTree* features = new TTree("features","Feature Extracted Data");

  Bool_t    FeatureExtractionActivated[2] ;
  Bool_t    WinError[2]                   ;
  Int_t     TBegin[2]                     ;
  Int_t     LE_time[2]                    ;
  Int_t     PeakTime[2]                   ;
  Int_t     TE_time[2]                    ;
  Int_t     TEnd[2]                       ;
  Int_t     APstartTime[2]                ;
  Int_t     APmaxTime[2]                  ;
  Int_t     SaturationCounts[2]           ;
  Int_t     PeakVal[2]                    ;
  Int_t     RiemannSum[2]                 ;
  Int_t     ADC_counts[2][128]            ; // raw data variables
  Float_t   dADC_counts[2][128]           ;
  Float_t   ddADC_counts[2][128]          ;

  features->Branch("FeatExtActivated", FeatureExtractionActivated, "FeatExtActivated[2]/O");
  features->Branch("WinError", WinError, "WinError[2]/O");
  features->Branch("TBegin", TBegin, "TBegin[2]/I");
  features->Branch("LE_time", LE_time, "LE_time[2]/I");
  features->Branch("PeakTime", PeakTime, "PeakTime[2]/I");
  features->Branch("TE_time", TE_time, "TE_time[2]/I");
  features->Branch("TEnd", TEnd, "TEnd[2]/I");
  features->Branch("APstartTime", APstartTime, "APstartTime[2]/I");
  features->Branch("APmaxTime", APmaxTime, "APmaxTime[2]/I");
  features->Branch("NumSampsInTopEighth", SaturationCounts, "NumSampsInTopEighth[2]/I");
  features->Branch("PeakVal", PeakVal, "PeakVal[2]/I");
  features->Branch("RiemannSum", RiemannSum, "RiemannSum[2]/I");
  features->Branch("ADC_counts", ADC_counts, "ADC_counts[2][128]/I");
  features->Branch("dADC_counts", dADC_counts, "dADC_counts[2][128]/F");
  features->Branch("ddADC_counts", ddADC_counts, "ddADC_counts[2][128]/F");



  int numEnt = tree->GetEntriesFast();
  for (int e=0; e<numEnt; e++) {
    tree->GetEntry(e);

    for (int i = 0; i < 2; i++) {
      FeatureExtractionActivated[i]  = false;
      WinError[i]                    = false;
      TBegin[i]                      = 0;
      LE_time[i]                     = 0;
      PeakTime[i]                    = 0;
      TE_time[i]                     = 0;
      TEnd[i]                        = 127;
      APstartTime[i]                 = 0;
      APmaxTime[i]                   = 0;
      SaturationCounts[i]            = 0;
      PeakVal[i]                     = 0;
      RiemannSum[i]                  = 0;
      for (int j = 0; j < 128; j++) {
        ADC_counts[i][j] = 0;
        dADC_counts[i][j] = 0.0;
        ddADC_counts[i][j] = 0.0;
      }
    }

    // CHANNEL LOOP
    for (int i=0; i<16; i++) {
      int ch;
      if (i==0) ch=0;
      else if (i==14) ch=1;
      else continue;


      int j_rev = 999, waitForTailScan = 128, SampHist[20];
      int tBegin = 0;
      int prox_LE_best=999, prox_TE_best=999;
      int vPeak = 15, tPeak = 0;
      bool foundTEnd = false;
      int APmax = 0;


      // --- CHECK WINDOW ALIGNMENT --- //
      for (int j = 31; j < 96; j+=32) {
        if (TMath::Abs(Sample[i][j+1]-2*Sample[i][j]+Sample[i][j-1])>50) {
          WinError[ch] = true;
        }
      }

      // --- SAMPLE LOOP AND FEATURE EXTRACTION --- //
      ADC_counts[ch][0] = Sample[i][0];
      ADC_counts[ch][1] = Sample[i][1];
      dADC_counts[ch][0] = 1.0*(Sample[i][1] - Sample[i][0]);
      dADC_counts[ch][1] = 0.5*(Sample[i][2] - Sample[i][0]);
      dADC_counts[ch][2] = 0.5*(Sample[i][3] - Sample[i][1]);
      ddADC_counts[ch][0] =  1.0*(dADC_counts[ch][1] - dADC_counts[ch][0]);
      ddADC_counts[ch][1] =  0.5*(dADC_counts[ch][2] - dADC_counts[ch][0]);
      int j=2;
      for (; j<126; j++) {
        ADC_counts[ch][j]   = Sample[i][j];
        dADC_counts[ch][j]  = 0.5*Sample[i][j+1] - 0.5*Sample[i][j-1];
        ddADC_counts[ch][j] = 0.25*Sample[i][j+2] - 0.5*Sample[i][j] - 0.25*Sample[i][j-2];


        // --- TURN-ON TIME --- //
        if (tBegin == 0 && dADC_counts[ch][j] > 2. && dADC_counts[ch][j-1] > 2. && dADC_counts[ch][j-2] > 2. ){
          TBegin[ch] = j-1;
          tBegin = j-1;
        }


        // --- TURN-OFF TIME --- //
        if (tBegin != 0 && ADC_counts[ch][j-1] >= 5 && ADC_counts[ch][j] <= 5 && dADC_counts[ch][j-1] <= 0 && dADC_counts[ch][j] <= 0) {
          TEnd[ch] = j-1;
          foundTEnd = true;
        }
        else if ((!foundTEnd && dADC_counts[ch][j-1] < 0 && dADC_counts[ch][j] < 0 && ddADC_counts[ch][j] > 0) ) {
          TEnd[ch] = j-1;
        }


        // --- PEAK FINDING ALGORITHM --- //
        if (Sample[i][j-1] > vPeak){ // Is it a peak AND well out of the noise?
          FeatureExtractionActivated[ch] = true;
          tPeak = j-1; // set peak time
          vPeak = Sample[i][j-1];
          for (int k = 0; k < 20; k++) SampHist[k] = 0;
          j_rev = 0;     // reset sample history and reverse counter
          LE_time[ch] = 0; // reset leading edge timing parameters
          TE_time[ch] = 0; // reset trailing edge timing parameters
          prox_TE_best = 999; //
          prox_LE_best = 999; //
          SaturationCounts[ch] = 1; // reset saturation counts
          waitForTailScan = 2;
          APstartTime[ch] = 0; APmaxTime[ch] = 0;
          foundTEnd = false;
          if (tPeak < 98) TEnd[ch] = tPeak + 30;
          else TEnd[ch] = 127;
        }


        // --- LEADING EDGE SCAN --- //
        if (j_rev<20 && (tPeak-j_rev)>=0) {

          SampHist[j_rev] = Sample[i][tPeak-j_rev];

          if (FeatureExtractionActivated[ch] && SampHist[j_rev]>(0.875*vPeak)) SaturationCounts[ch]++;

          if (TMath::Abs(SampHist[j_rev]-(int)(0.5*vPeak)) < prox_LE_best){
            LE_time[ch] = tPeak-j_rev;
            prox_LE_best = TMath::Abs(SampHist[j_rev]-(int)(0.5*vPeak));
          }
        }
        j_rev++;


        // --- TAIL EDGE SCAN --- //
        if (FeatureExtractionActivated[ch] && waitForTailScan<1) {

          if (dADC_counts[ch][j-2] > 3 && dADC_counts[ch][j-1] > 3 && dADC_counts[ch][j] > 3 && APstartTime[ch] == 0){
            APstartTime[ch] = j-2;
            APmaxTime[ch] = j;
            APmax = Sample[i][j];
          }
          if (APstartTime[ch] != 0 && Sample[i][j] > APmax) {
            APmax = Sample[i][j];
            APmaxTime[ch] = j;
          }

          if (TMath::Abs(Sample[i][j]-(int)(0.5*vPeak)) < prox_TE_best){
            TE_time[ch] = j;
            prox_TE_best = TMath::Abs(Sample[i][j]-(int)(0.5*vPeak));

          }

        }
        waitForTailScan--;

        if (FeatureExtractionActivated[ch] && Sample[i][j]>(int)(0.875*vPeak)) SaturationCounts[ch]++; // increment saturation Counter

      }// END SAMP LOOP

      while (j < 128) {
        if (APstartTime[ch] != 0 && Sample[i][j] > APmax) {
          APmax = Sample[i][j];
          APmaxTime[ch] = j;
        }
        j++;
      }

      for (int t = tBegin; t <= TEnd[ch]; t++) {
        RiemannSum[ch] += ADC_counts[ch][t];
      }
      TBegin[ch] = tBegin;
      PeakVal[ch]  = vPeak;
      PeakTime[ch] = tPeak;
    }// END CH LOOP
    features->Fill();

  }// END EVENT LOOP
  printf("Processed %d Events.\n",numEnt);
  file->Write("features");
}
