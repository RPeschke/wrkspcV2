#ifndef extract_efficiency_h__
#define extract_efficiency_h__
#include "KLM_lib/Platform.hh"
#include <string>
#include "TTree.h"
#include <vector>
#include <memory>
#include <map>

class DLLEXPORT ttree_filter {
public:
	double m_nominal_value;
	std::string name;
	std::string filter;


};
DLLEXPORT std::vector<ttree_filter> filter_gt(std::string var, double);
DLLEXPORT std::vector<ttree_filter> filter_lt(std::string var, double);
DLLEXPORT std::vector<ttree_filter> condition(std::string var, double);

DLLEXPORT std::vector<ttree_filter> operator+(std::vector<ttree_filter> in1, std::vector<ttree_filter> in2);

class DLLEXPORT ttree_filter_branch {
public:
	ttree_filter_branch(TTree* out,std::string prefix = "");
	ttree_filter_branch& operator<<(const std::vector<ttree_filter>& filter);

private:
#ifndef __CINT__
	TTree * m_out;
	bool first = true;
	std::map<std::string,std::shared_ptr<double>>  m_data;
	std::string m_prefix;
#endif
};

class DLLEXPORT efficiency { 
public:
	
	double m_efficiency;
	double m_error;
	std::vector<ttree_filter> input_filter , reference_filter;

};


DLLEXPORT efficiency extract_efficiency(
	TTree* inputTree, 
	std::vector<ttree_filter> Input_Filter = std::vector<ttree_filter>(), 
	TTree* referenceTree = 0, 
	std::vector<ttree_filter> reference_filter = std::vector<ttree_filter>()
);

class DLLEXPORT ttree_efficiency_branch {
public:
	ttree_efficiency_branch(TTree* out);
	ttree_efficiency_branch& operator<<(const efficiency&);
	void Fill();

private:
#ifndef __CINT__
	std::shared_ptr<double> m_efficiency, m_error;
	ttree_filter_branch input_filter, reference_filter;
	TTree* m_tree;
#endif
};

DLLEXPORT void extract_efficiency_to_ttree(const std::string& inFileName, const std::string& outFileName, std::vector<ttree_filter> Input_Filter = std::vector<ttree_filter>());
DLLEXPORT void extract_efficiency_to_ttree2(TFile* inFileName, ttree_efficiency_branch& out_branch , std::vector<ttree_filter> Input_Filter = std::vector<ttree_filter>());
#endif // extract_efficiency_h__
