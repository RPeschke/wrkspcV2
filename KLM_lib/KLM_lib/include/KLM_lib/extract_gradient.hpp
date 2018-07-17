#ifndef extract_gradient_h__
#define extract_gradient_h__
#include "KLM_lib/Platform.hh"
#include <vector>



std::vector<int> ROOTFUNCTION extract_gradient(const std::vector<int>& wave);

std::vector<double> ROOTFUNCTION extract_gradient_Accuracy2(const std::vector<int>& wave);


std::vector<double> ROOTFUNCTION extract_gradient_Accuracy4(const std::vector<int>& wave);

std::vector<double> ROOTFUNCTION extract_gradient_Accuracy6(const std::vector<int>& wave);



#endif // extract_gradient_h__
