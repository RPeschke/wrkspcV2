#include "Riostream.h"
#include "TMath.h"

void ProcessWaveformData(const char* root_input, const char* root_output) {

  // TTree Variables
  Int_t   EvtNum, AddNum,  WrAddNum, Wctime, ASIC, tFW, qFW, Sample[16][128]; // raw data variables
  Bool_t  FeatureExtractionActivated[16]  = {false};
  Float_t Time[16]                        = {0.0};
  Float_t TimeOverThr[16]                 = {0.0};
  Int_t   StrtnCnts[16]                   = {0};
  Bool_t  AfterPulseFlag[16]              = {false};
  Int_t   AfterPulseRelativeAmplitude[16] = {0};
  Int_t   PeakVal[16]                     = {0};

  // peak finding variables
  int tempPeak=0, peakTime, diffL, diffR;

  // leading edge timing variables
  int SampHist[10], tLowerThr=0, tHigherThr=0, proxToLowerThr, proxToHigherThr, proxLowerThrBest=999, proxHigherThrBest=999;

  // tail edge variables
  int waitForTailScan, APmax, APstartVal;
  int tLowerThrTail=0, tHigherThrTail=0, proxLowerThrBestTail=999, proxHigherThrBestTail=999;

  TFile* InFile = new TFile(root_input, "READ");
  TTree* InTree = (TTree*)InFile->Get("tree");

  InTree->SetBranchAddress("EvtNum", &EvtNum);
  InTree->SetBranchAddress("AddNum", &AddNum);
  InTree->SetBranchAddress("WrAddNum", &WrAddNum);
  InTree->SetBranchAddress("Wctime", &Wctime);
  InTree->SetBranchAddress("ASIC", &ASIC);
  InTree->SetBranchAddress("ADC_counts", Sample);

  TFile* OutFile = new TFile(root_output, "RECREATE");
  TTree* OutTree = new TTree("tree","Feature Extracted Data");

  OutTree->Branch("FeatExtActivated", FeatureExtractionActivated, "FeatExtActivated[16]/O");
  OutTree->Branch("PeakVal", PeakVal, "PeakVal[16]/I");
  OutTree->Branch("NumSampsInTopEighth", StrtnCnts, "NumSampsInTopEighth[16]/I");
  OutTree->Branch("Time", Time, "Time[16]/F");
  OutTree->Branch("AfterPulseFlag", AfterPulseFlag, "AfterPulseFlag[16]/O");
  OutTree->Branch("AfterPulseRelativeAmplitude", AfterPulseRelativeAmplitude, "AfterPulseRelativeAmplitude[16]/I");
  OutTree->Branch("TimeOverThr", TimeOverThr, "TimeOverThr[16]/F");

  int nlines = 0;
  int tempSamp = 0, offset = 0;
  int j_rev = 999;

  InFile->cd();
  int numEnt = InTree->GetEntriesFast();
  for (int e=0; e<numEnt; e++) {
    InFile->cd();
    InTree->GetEntry(e);
    for (int i=0; i<16; i++) {
      tempPeak  = 0; tHigherThr = 0; tLowerThr = 0; j_rev = 999; waitForTailScan=128; // housekeeping
      FeatureExtractionActivated[i] = false; AfterPulseFlag[i] = false; // TTree variables!
      // --- SAMPLE LOOP AND FEATURE EXTRACTION --- //
      for (int j=2; j<128; j++) {
        // --- PEAK FINDING ALGORITHM --- //
        if (Sample[i][j-1]>tempPeak && Sample[i][j-1]>30){ // Is it a peak AND well out of the noise?
          FeatureExtractionActivated[i] = true;
          peakTime = j-1; // set peak time
          diffL = Sample[i][j-1]-Sample[i][j-2]; // difference to sample left
          diffR = Sample[i][j-1]-Sample[i][j]; // difference to sample right
          // check for outliers. If none, then assign peak.
          if (diffL < 20 && diffR < 20) tempPeak = Sample[i][j-1];
          // if outliers, throw away outlier then avg. neighboring samples
          else tempPeak = (Sample[i][j-2]+Sample[i][j])/2;
          int SampHist[20] = {0}; j_rev = 0;     // reset sample history and reverse counter
          tHigherThr   = 0; proxLowerThrBest = 999;  // reset leading edge timing parameters
          tLowerThr    = 0; proxHigherThrBest = 999; //
          tHigherThrTail   = 0; proxLowerThrBestTail = 999;  // reset leading edge timing parameters
          tLowerThrTail    = 0; proxHigherThrBestTail = 999; //
          StrtnCnts[i] = 1; // reset saturation counts
          waitForTailScan = 2;
          AfterPulseFlag[i] = false; AfterPulseRelativeAmplitude[i] = 0;
        }
        // --- LEADING EDGE SCAN --- //
        if (j_rev<10 && (peakTime-j_rev)>=0) {
          SampHist[j_rev] = Sample[i][peakTime-j_rev];
          if (FeatureExtractionActivated[i] && SampHist[j_rev]>(int)(0.875*tempPeak)) StrtnCnts[i]++;
          proxToHigherThr = TMath::Abs(SampHist[j_rev]-110);
          if (proxToHigherThr<proxHigherThrBest){
            tHigherThr = peakTime-j_rev;
            proxHigherThrBest = proxToHigherThr;
          }
          proxToLowerThr = TMath::Abs(SampHist[j_rev]-90);
          if (proxToLowerThr<proxLowerThrBest){
            tLowerThr = peakTime-j_rev;
            proxLowerThrBest = proxToLowerThr;
          }
        }
        // --- TAIL EDGE SCAN --- //
        if (j<128 && FeatureExtractionActivated[i] && waitForTailScan<1) {
          if (Sample[i][j]>Sample[i][j-1] && Sample[i][j-1]>Sample[i][j-2] && !AfterPulseFlag[i]){
            AfterPulseFlag[i] = true;
            APmax=Sample[i][j];
            APstartVal = Sample[i][j-2];
          }
          if (AfterPulseFlag[i] && Sample[i][j]>APmax) {
            APmax=Sample[i][j];
            AfterPulseRelativeAmplitude[i] = APmax - APstartVal;
          }
          proxToHigherThr = TMath::Abs(Sample[i][j]-110);
          if (proxToHigherThr<proxHigherThrBestTail){
            tHigherThrTail = j;
            proxHigherThrBestTail = proxToHigherThr;
          }
          proxToLowerThr = TMath::Abs(Sample[i][j]-90);
          if (proxToLowerThr<proxLowerThrBestTail){
            tLowerThrTail = j;
            proxLowerThrBestTail = proxToLowerThr;
          }

        }

        if (FeatureExtractionActivated[i] && Sample[i][j]>(int)(0.875*tempPeak)) StrtnCnts[i]++; // increment saturation Counter
        waitForTailScan--;
        j_rev++;
      }// END SAMP LOOP
      Time[i] = 0.5*tLowerThr + 0.5*tHigherThr;
      TimeOverThr[i]  = 0.5*tLowerThrTail + 0.5*tHigherThrTail - Time[i];
      PeakVal[i] = tempPeak;
    }// END CH LOOP
    OutFile->cd();
    OutTree->Fill();
  }// END EVENT LOOP
  printf("Processed %d Events.\n",numEnt);
  InFile->cd();  InFile->Close();
  OutFile->cd(); OutFile->Write("tree");
  OutFile->Close();
}
