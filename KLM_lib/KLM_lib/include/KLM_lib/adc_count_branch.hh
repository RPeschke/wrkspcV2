#ifndef adc_count_branch_h__
#define adc_count_branch_h__
#include <string>
#include <vector>
#include "TTree.h"


inline std::string make_branch_name(const std::string& b_name, size_t size, int*) {
  std::string ret = b_name;
  ret += "[" + std::to_string(size) + "]/I";
  return ret;
}

inline std::string make_branch_name(const std::string& b_name, size_t size, double*) {
  std::string ret = b_name;
  ret += "[" + std::to_string(size) + "]/D";
  return ret;
}

template <typename T>
class adc_count_branch {
private:
  T* adc_counts;
	const int m_size;

public:
	inline adc_count_branch(TTree* out_tree, const std::string& name, int size_ = 128): m_size(size_) {
		adc_counts = new T[size_];
		out_tree->Branch(name.c_str(), adc_counts, make_branch_name(name,size_,adc_counts).c_str());

	}
	virtual inline ~adc_count_branch() {
		delete[] adc_counts;
	}

	friend inline adc_count_branch& operator<<(adc_count_branch& out, const std::vector<T>& f) {
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
	friend inline adc_count_branch& operator<<(adc_count_branch& out, T* f) {

 
		for (int i = 0; i < out.m_size; ++i)
		{
			out.adc_counts[i] = f[i];
		}

		return out;
	}
};

#endif // adc_count_branch_h__
