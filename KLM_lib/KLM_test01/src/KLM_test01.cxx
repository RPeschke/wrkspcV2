#include <iostream>
#include "KLM_lib/Feature_extraction.hpp"
#include "KLM_lib/extract_efficiency.hpp"


int main() {

	auto out_file = new TFile("efficiency.root", "recreate");
	auto tree = new TTree("effi", "effi");
	ttree_efficiency_branch branch_effi(tree);
	
	
	TFile *_file0 = TFile::Open("../../features_HV136.root");
	extract_efficiency_to_ttree2(_file0, branch_effi , condition("HV_DAC",136 ) );

	_file0 = TFile::Open("../../features_HV138.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 138));

	_file0 = TFile::Open("../../features_HV140.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 140));

	_file0 = TFile::Open("../../features_HV142.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 142));

	_file0 = TFile::Open("../../features_HV144.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 144));

	_file0 = TFile::Open("../../features_HV146.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 146));
	_file0 = TFile::Open("../../features_HV148.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 148));

	_file0 = TFile::Open("../../features_HV150.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 150));

	_file0 = TFile::Open("../../features_HV152.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 152));

	_file0 = TFile::Open("../../features_HV154.root");
	extract_efficiency_to_ttree2(_file0, branch_effi, condition("HV_DAC", 154));

	out_file->Write();
	return 1;

}