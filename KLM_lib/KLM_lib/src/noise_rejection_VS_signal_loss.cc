#include "KLM_lib/noise_rejection_VS_signal_loss.hpp"
#include "KLM_lib/Integrate_TH1.hpp"

#include <fstream>

TGraph noise_rejection_VS_signal_loss(TH1* NoiseSpectrum, TH1* SignalSpectrum,double step)
{
	
	TGraph ret;

	std::ofstream out("out.txt");


	auto intNoise = Integrate_TH1(NoiseSpectrum, true);
	
	auto intSignal = Integrate_TH1(SignalSpectrum);

	for (double x =  
		-5
		//intNoise.GetXaxis()->GetBinLowEdge(1)
		; x < intSignal.GetXaxis()->GetBinLowEdge(intSignal.GetNbinsX() + 1) ; x+=step){
		ret.SetPoint(ret.GetN(), intNoise.Interpolate(x), intSignal.Interpolate(x));
		out << x << ", " << intNoise.Interpolate(x) << ",  " << intSignal.Interpolate(x) << std::endl;
	}

	return ret;
}
