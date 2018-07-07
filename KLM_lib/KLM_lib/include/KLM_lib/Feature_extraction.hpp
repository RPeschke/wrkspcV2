#ifndef Feature_extraction_h__
#define Feature_extraction_h__

#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>
#include <string>

#include "TGraph.h"
#include "TFile.h"

#include "extract_peak.hh"
#include "helper_int_vector.hh"
#include "filter_waveform.hh"
#include "extract_area.hh"
#include "extract_edges.hh"
#include "adc_count_branch.hh"
#include "KLM_Tree.hpp"
#include "Platform.hh"

DLLEXPORT void Feature_extraction_read_file(const std::string& fileName, const std::string& TreeName, int channelNr,TFile* out);
DLLEXPORT void Feature_extraction_read_file2(const std::string& fileName, const std::string& fileNameOut);
#endif // Feature_extraction_h__
