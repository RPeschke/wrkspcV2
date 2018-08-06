#include "Riostream.h"
#include "TMath.h"
#include <cstdio>
#include "string.h"

string WinErr = "Window Alignment Error";
string AftPul = "After Pulse Detected";

void FeatureMarker(TH1D* hist, double x, double y, Color_t color){
  TMarker *MARK;
  MARK = new TMarker(x,y,kFullCross);
  MARK->SetMarkerColorAlpha(color, 0.25);
  MARK->SetMarkerSize(3);
  hist->GetListOfFunctions()->Add(MARK);
}

void WaitForUserInput(){ char ks = getchar(); if (ks=='q') exit(-1); }

void AddText(TH1D* hist, double x, double y, Color_t color, const char* text){
  TText *TXT = new TText(x, y, text);
  TXT->SetNDC();
  TXT->SetTextFont(1);
  TXT->SetTextColor(color);
  TXT->SetTextSize(0.08);
  TXT->SetTextAlign(22);
  TXT->SetTextAngle(0);
  hist->GetListOfFunctions()->Add(TXT);
}

void PlotFeatures(const char* root_input) {

  // TTree Variables
  Int_t     ADC_counts[2][128];
  Float_t   dADC_counts[2][128];
  Float_t   ddADC_counts[2][128];
  Bool_t    FeatExtActivated[2]            = {false};
  Bool_t    WinError[2]                    = {false};
  Int_t     TBegin[2]                      = {0};
  Int_t     LE_time[2]                      = {0};
  Int_t     TE_time[2]                      = {0};
  Int_t     TEnd[2]                        = {0};
  Int_t     StrtnCnts[2]                   = {0};
  Int_t     APstartTime[2]                 = {0};
  Int_t     APmaxTime[2]                   = {0};
  Int_t     PeakVal[2]                     = {0};
  Int_t     PeakTime[2]                    = {0};
  Int_t     RiemannSum[2]                  = {0};

  TFile* file = new TFile(root_input, "READ");
  TTree* tree = (TTree*)file->Get("features");

  tree->SetBranchAddress("ADC_counts", ADC_counts);
  tree->SetBranchAddress("dADC_counts", dADC_counts);
  tree->SetBranchAddress("ddADC_counts", ddADC_counts);
  tree->SetBranchAddress("FeatExtActivated", FeatExtActivated);
  tree->SetBranchAddress("WinError", WinError);
  tree->SetBranchAddress("PeakVal", PeakVal);
  tree->SetBranchAddress("PeakTime", PeakTime);
  tree->SetBranchAddress("TBegin", TBegin);
  tree->SetBranchAddress("LE_time", LE_time);
  tree->SetBranchAddress("TE_time", TE_time);
  tree->SetBranchAddress("TEnd", TEnd);
  tree->SetBranchAddress("NumSampsInTopEighth", StrtnCnts);
  tree->SetBranchAddress("APstartTime", APstartTime);
  tree->SetBranchAddress("APmaxTime", APmaxTime);
  tree->SetBranchAddress("RiemannSum", RiemannSum);

  TH1D* hist[2];
  for (size_t i = 0; i < 2; i++) {
    hist[i] = new TH1D("", "", 128,0,128);
    hist[i]->GetYaxis()->SetTitleOffset(1.5);
    hist[i]->GetYaxis()->SetTitle("ADC Counts");
    hist[i]->SetMarkerStyle(8);
    hist[i]->SetMaximum(650);
    hist[i]->SetMinimum(-50);
  }

  TCanvas *canv = new TCanvas("canv","features",1100,550);
  canv->Divide(1,2);

  cout << "\033[1;96mPress \033[92m<ENTER>\033[1;96m to see next plot\nPress \033[1;91m'q'\033[1;96m to quit\033[m\n";
  int NumEvts = tree->GetEntriesFast();
  for (int e=0; e<NumEvts; e++) {
    tree->GetEntry(e);
    for (int i = 0; i < 2; i++) {
      hist[i]->Reset();
      for (int j=0; j<128; j++) {
        hist[i]->SetBinContent(j,ADC_counts[i][j]);
      }
      if (WinError[i])       AddText(hist[i], 0.25, 0.85, kRed, WinErr.c_str());
      if (APstartTime[i] != 0) AddText(hist[i], 0.25, 0.75, kRed, AftPul.c_str());
      FeatureMarker( hist[i], (double)TBegin[i]  , (double)(ADC_counts[i][TBegin[i]]), kViolet );
      FeatureMarker( hist[i], (double)LE_time[i] , (double)(0.50*(PeakVal[i]))       , kBlue   );
      FeatureMarker( hist[i], (double)PeakTime[i], (double)(PeakVal[i])              , kGreen  );
      FeatureMarker( hist[i], (double)TE_time[i] , (double)(0.50*(PeakVal[i]))       , kRed    );
      FeatureMarker( hist[i], (double)TEnd[i]    , (double)(ADC_counts[i][TEnd[i]])  , kAzure  );
      if (APstartTime[i] != 0){
        FeatureMarker( hist[i], (double)APstartTime[i], (double)ADC_counts[i][APstartTime[i]],   kYellow );
        FeatureMarker( hist[i], (double)APmaxTime[i]  , (double)ADC_counts[i][APmaxTime[i]]  ,   kOrange  );
      }
      cout << TBegin[i]  << " " << LE_time[i]  << " " << PeakTime[i] << " " << TE_time[i]  << " " << TEnd[i]  << endl;
      canv->cd(i+1); hist[i]->Draw("P");
      canv->Update();
    }
    WaitForUserInput();
  }
}
