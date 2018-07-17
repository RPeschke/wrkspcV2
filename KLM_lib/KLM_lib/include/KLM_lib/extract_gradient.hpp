#ifndef extract_gradient_h__
#define extract_gradient_h__
#include "KLM_lib/Platform.hh"
#include <vector>



DLLEXPORT std::vector<int> extract_gradient(const std::vector<int>& wave);

DLLEXPORT std::vector<double> extract_gradient_Accuracy2(const std::vector<int>& wave);


DLLEXPORT std::vector<double> extract_gradient_Accuracy4(const std::vector<int>& wave);

DLLEXPORT std::vector<double> extract_gradient_Accuracy6(const std::vector<int>& wave);

#pragma link C++ function extract_gradient;
#pragma link C++ function extract_gradient_Accuracy2;
#pragma link C++ function extract_gradient_Accuracy4;
#pragma link C++ function extract_gradient_Accuracy6;

#endif // extract_gradient_h__
