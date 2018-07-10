#include <string>
#include "TAxis.h"
#include "KLM_lib/Integrate_TH1.hpp"

TH1D Integrate_TH1(TH1* inHist,bool reverse)
{
	TH1D ret( (std::string("int_")+  inHist->GetName()).c_str() , (std::string("Integral of ") + inHist->GetTitle()).c_str() ,inHist->GetNbinsX(), inHist->GetXaxis()->GetBinLowEdge(1), inHist->GetXaxis()->GetBinLowEdge(inHist->GetNbinsX()+1));

	double sum = 0;
	const double totalSum = inHist->Integral();
	if (reverse)	{
		for (int i = inHist->GetNbinsX() + 1; i >= 0; --i) {
			sum += inHist->GetBinContent(i) / totalSum;
			ret.Fill(inHist->GetXaxis()->GetBinCenter(i), sum);

		}
	}
	else {
		for (int i = 0; i < inHist->GetNbinsX() + 1; ++i) {
			sum += inHist->GetBinContent(i) / totalSum;
			ret.Fill(inHist->GetXaxis()->GetBinCenter(i), sum);

		}
	}
	return ret;
}

