#ifndef noise_rejection_VS_signal_loss_h__
#define noise_rejection_VS_signal_loss_h__
#include "TGraph.h"
#include "KLM_lib/Platform.hh"

TGraph ROOTFUNCTION noise_rejection_VS_signal_loss(TH1* NoiseSpectrum, TH1* SignalSpectrum,double step = 1);



#endif // noise_rejection_VS_signal_loss_h__
