#include "KLM_lib/extract_efficiency.hpp"
#include "TMath.h"
#include "TFile.h"


std::vector<ttree_filter> filter_gt(std::string var, double value)
{
	ttree_filter ret;
	ret.m_nominal_value = value;
	ret.name = var + "_gt";
	ret.filter = var + ">" + std::to_string(value);
	return std::vector<ttree_filter>{ret};
}

std::vector<ttree_filter> filter_lt(std::string var, double value)
{
	ttree_filter ret;
	ret.m_nominal_value = value;
	ret.name = var + "_lt";
	ret.filter = var + "<" + std::to_string(value);
	return std::vector<ttree_filter>{ret};
}

std::vector<ttree_filter> condition(std::string var, double value)
{
	ttree_filter ret;
	ret.m_nominal_value = value;
	ret.name = "con_" + var;
	return std::vector<ttree_filter>{ret};
}

std::vector<ttree_filter> operator+(std::vector<ttree_filter> in1, std::vector<ttree_filter> in2)
{
	for (cautor e : in2) {
		in1.push_back(e);
	}
	return in1;
}

efficiency extract_efficiency(TTree* inputTree, std::vector<ttree_filter> Input_Filter, TTree* referenceTree , std::vector<ttree_filter> reference_filter /*=""*/)
{
	std::string ref_filter = "1";
	for (cautor e : reference_filter) {
		if (!e.filter.empty()) {
			ref_filter += "&&(" + e.filter + ")";
		}
	}
	auto nref = (double) referenceTree->GetEntries(ref_filter.c_str());


	for (cautor e : Input_Filter) {
		if (!e.filter.empty()) {
			ref_filter += "&&(" + e.filter + ")";
		}
	}
	auto N = (double)inputTree->GetEntries(ref_filter.c_str());

	efficiency ret;
	ret.m_efficiency = N / nref;

	ret.m_error = TMath::Sqrt(N + (N*N) / nref) / nref;

	ret.input_filter = Input_Filter;
	ret.reference_filter = reference_filter;
	return ret;
}

ttree_filter_branch::ttree_filter_branch(TTree* out, std::string prefix):m_out(out),m_prefix(prefix)
{
	
}

ttree_filter_branch& ttree_filter_branch::operator<<(const std::vector<ttree_filter>& filter)
{
	if (first){
		for (cautor e : filter)
		{
			auto var = std::make_shared<double>(0);
			m_data[e.name] =  var;
			m_out->Branch((m_prefix + e.name).c_str(), var.get());

		}
		first = false;
	}
	for (cautor e : filter)
	{
		*(m_data[e.name]) = e.m_nominal_value;
	}

	return *this;
}


ttree_efficiency_branch::ttree_efficiency_branch(TTree* out):input_filter(out),reference_filter(out,"ref_"), m_tree(out)
{
	m_efficiency = std::make_shared<double>(0);
	m_error = std::make_shared<double>(0);
	out->Branch("efficiency", m_efficiency.get());
	out->Branch("error", m_error.get());
}

ttree_efficiency_branch& ttree_efficiency_branch::operator<<(const efficiency& eff)
{
	*m_efficiency = eff.m_efficiency;
	*m_error = eff.m_error;
	input_filter << eff.input_filter;
	reference_filter << eff.reference_filter;
	return *this;

}

void ttree_efficiency_branch::Fill()
{
	m_tree->Fill();
}

void extract_efficiency_to_ttree(const std::string& inFileName, const std::string& outFileName, std::vector<ttree_filter> Input_Filter) {
	TFile *_file0 = TFile::Open(inFileName.c_str());

	auto out_file = new TFile(outFileName.c_str(), "recreate");
	auto tree = new TTree("efficiency", "efficiency");
	ttree_efficiency_branch branch_effi(tree);
	extract_efficiency_to_ttree2(_file0, branch_effi,Input_Filter);

	out_file->Write();
}

void extract_efficiency_to_ttree2(TFile* inFileName, ttree_efficiency_branch& out_branch, std::vector<ttree_filter> Input_Filter /*= std::vector<ttree_filter>()*/)
{
	for (int j = -10000; j < 1; j += 10000)
	{
		for (int i = 0; i < 600; i += 10)
		{
			auto x5 = extract_efficiency(
				(TTree*)inFileName->Get("features_14"),
				filter_gt("rising_edge_time", j) + filter_gt("peak_signal", i) + Input_Filter,
				(TTree*)inFileName->Get("features_0")

			);

			out_branch << x5;

			out_branch.Fill();
		}
	}

}
