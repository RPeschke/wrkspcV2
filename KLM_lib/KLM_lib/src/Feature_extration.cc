#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>


#include "TGraph.h"

#include "KLM_lib/extract_peak.hh"
#include "KLM_lib/helper_int_vector.hh"
#include "KLM_lib/filter_waveform.hh"
#include "KLM_lib/extract_area.hh"
#include "KLM_lib/extract_edges.hh"

#include "KLM_lib/Feature_extraction.hpp"






std::vector<int> get_x() {
	std::vector<int> ret;
	for (int i = 0; i < 128; i++)
	{
		ret.push_back(i);
	}
	return ret;
}

void Feature_extraction_read_file(const std::string& fileName, const std::string& TreeName, int ChannelNr, TFile* outFile) {


	TFile *_file0 = TFile::Open(fileName.c_str());
	auto tree = dynamic_cast<TTree*>(_file0->Get(TreeName.c_str()));

	auto t1 = new  KLM_Tree(tree);



	auto out_tree = [&] {
		outFile->cd();
		std::string branch_name = "features_" + std::to_string(ChannelNr);
		return  new TTree(branch_name.c_str(), branch_name.c_str());
	}();

	//out_tree->SetDirectory(outFile->GetDirectory());
	feature_branch counter_branch(out_tree, "counter");
	feature_branch branch_peak(out_tree, "peak");
	feature_branch branch_falling_edge(out_tree, "falling_edge");
	feature_branch branch_rising_edge(out_tree, "rising_edge");
	feature_branch branch_TOT(out_tree, "TOT");
	adc_count_branch branch_adc(out_tree, "adc_counts");
	adc_count_branch branch_adc_x(out_tree, "adc_x");

	branch_adc_x << get_x();

	for (int i = 0; i < tree->GetEntries() - 1; ++i) {


		t1->GetEntry(i);
		auto vec = to_vector(t1->ADC_counts[ChannelNr]);
		auto vec1 = filter_waveform(vec, 100);
		branch_peak << extract_peak(vec1);
		branch_falling_edge << extract_faling_edge(vec1, 202, 250);

		branch_rising_edge << extract_rising_edge(vec1, 200, 100);

		feature counter;
		counter.signal = i;
		counter.time = i;
		counter_branch << counter;

		branch_TOT << extract_time_over_threshold(vec1, 200, 250);

		branch_adc << t1->ADC_counts[ChannelNr];
		out_tree->Fill();

	}

	//   out_tree->Write();
	std::cout << "fout->Write();\n";
	outFile->Write();
	std::cout << "/fout->Write();\n";

}


void Feature_extraction_read_file2(const std::string& fileName, const std::string& fileNameOut)
{
	TFile out1(fileNameOut.c_str(), "RECREATE");
	Feature_extraction_read_file(fileName.c_str(), "tree", 14, &out1);
	Feature_extraction_read_file(fileName.c_str(), "tree", 0, &out1);
}

