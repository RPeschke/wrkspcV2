#ifndef adc_count_branch_h__
#define adc_count_branch_h__
#include <string>
#include <vector>
#include "TTree.h"

class adc_count_branch {
private:
	int* adc_counts;
	const int m_size;

public:
	inline adc_count_branch(TTree* out_tree, const std::string& name, int size_ = 128): m_size(size_) {
		adc_counts = new int[size_];
		out_tree->Branch(name.c_str(), adc_counts, "ADC_counts[128]/I");

	}
	virtual inline ~adc_count_branch() {
		delete[] adc_counts;
	}

	friend inline adc_count_branch& operator<<(adc_count_branch& out, const std::vector<int>& f) {
		if (f.size() < out.m_size)
		{
			std::cout << "Unable to store data in branch: Input vector to small\n";
			return out;
		}
		for (int i =0 ; i < out.m_size ; ++i)
		{
			out.adc_counts[i] = f[i];
		}
		

		return out;
	}
	friend inline adc_count_branch& operator<<(adc_count_branch& out, int* f) {

 
		for (int i = 0; i < out.m_size; ++i)
		{
			out.adc_counts[i] = f[i];
		}

		return out;
	}
};

#endif // adc_count_branch_h__
