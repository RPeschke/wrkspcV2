#include "KLM_lib/extract_gradient.hpp"
#include <iostream>
std::vector<int> extract_gradient(const std::vector<int>& wave)
{
  std::vector<int> ret;
  ret.reserve((wave.size()));
  ret.push_back(wave[1]-wave[0]);
  for (int i = 1; i < wave.size();i++) {
    ret.push_back(wave[i] - wave[i-1]);
  }
  return ret;
}



std::vector<double> extract_gradient_Accuracy2(const std::vector<int>& wave)
{
  std::vector<double> ret(wave.size());
  
  
  for (int i = 1; i < wave.size()-1; i++) {
    ret[i] = -0.5 * wave[i - 1] + 0.5* wave[i + 1];
  }
  ret.push_back(0);

  return ret;

}

std::vector<double> extract_gradient_Accuracy4(const std::vector<int>& wave)
{
  std::vector<double> ret(wave.size());
  
  for (int i = 2; i < wave.size() - 2; i++) {
    ret[i] = +1.0/12 * wave[i - 2]  -2.0/3 * wave[i-1] + 2.0/3 * wave[i + 1] - 1.0/12 * wave[i+2] ;
  }


  return ret;
}


std::vector<double> extract_gradient_Accuracy6(const std::vector<int>& wave)
{
  std::vector<double> ret(wave.size());

  for (int i = 3; i < wave.size() - 3; i++) {
    ret[i] = -1.0 / 60 * wave[i - 3] + 3.0 / 20 * wave[i - 2] - 3.0 / 4 * wave[i - 1] + 3.0 / 4 * wave[i + 1] - 3.0 / 20 * wave[i + 2] + 1.0 / 60 * wave[i + 3];
  }


  return ret;
}
