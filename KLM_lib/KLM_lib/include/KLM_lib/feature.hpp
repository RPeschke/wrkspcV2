#ifndef feature_h__
#define feature_h__
#include <string>
#include <iostream>
#include "TGraph.h"
#include "TTree.h"
#include "KLM_lib/Platform.hh"

class feature {
public:
	double time = -100, signal = -100;
	TGraph* Draw(std::string options = "*");
};

std::ostream& operator<<(std::ostream& out, const feature& f);




class DLLEXPORT feature_branch {
public:
	feature_branch(TTree* out_tree,const std::string& name);
	feature_branch(const std::string& name);
	virtual ~feature_branch();
	
	void set_input_tree(TTree* tree);
	feature_branch& operator<<(const feature& f);
	const feature_branch& operator>>( feature& f) const ;
private:
	feature* m_feature;
	std::string m_name;
};

#endif // feature_h__
