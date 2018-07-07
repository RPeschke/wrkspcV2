#include "KLM_lib/feature.hpp"

std::ostream& operator<<(std::ostream& out, const feature& f)
{
	out << "time: " << f.time << " Signal: " << f.signal;
	return out;
}

 TGraph* feature::Draw(std::string options /*= "*"*/)
{
	TGraph* ret = new TGraph();
	ret->SetPoint(ret->GetN(), time, signal);
	ret->SetMarkerColor(4);
	ret->Draw(options.c_str());
	return ret;
}

 feature_branch::feature_branch(TTree* out_tree, const std::string& name) :m_name(name)
 {
	 m_feature = new feature();
	 out_tree->Branch((name + "_signal").c_str(), &m_feature->signal);
	 out_tree->Branch((name + "_time").c_str(), &m_feature->time);
 }

 feature_branch::feature_branch(const std::string& name) :m_name(name)
 {
	 m_feature = new feature();
 }

 feature_branch::~feature_branch()
 {
	 delete m_feature;
 }

 void feature_branch::set_input_tree(TTree* tree)
 {
	 tree->SetBranchAddress((m_name + "_signal").c_str(), &m_feature->signal);
	 tree->SetBranchAddress((m_name + "_time").c_str(), &m_feature->time);
 }

 feature_branch& feature_branch::operator<<(const feature& f)
 {
	 m_feature->signal = f.signal;


	 m_feature->time = f.time;


	 return *this;
 }

 const feature_branch& feature_branch::operator>>( feature& f) const
 {
	 f.signal = m_feature->signal;


	  f.time = m_feature->time;


	 return *this;
 }
