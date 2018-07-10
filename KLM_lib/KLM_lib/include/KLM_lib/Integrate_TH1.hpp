#ifndef Integrate_TH1_h__
#define Integrate_TH1_h__
#include "TH1D.h"
#include "KLM_lib/Platform.hh"

DLLEXPORT TH1D Integrate_TH1(TH1* inHist,bool reverse =false);




#pragma link C++ function Integrate_TH1;

#endif // Integrate_TH1_h__
