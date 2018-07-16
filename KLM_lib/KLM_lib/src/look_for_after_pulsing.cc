#include "KLM_lib/look_for_after_pulsing.hh"
#include "KLM_lib/extract_peak.hh"

feature look_for_after_pulsing(const std::vector<int>& ADC_counts){

	feature after_pulse;

  auto peak = extract_peak(ADC_counts);
  bool APflag = false;
  int APmax = 0, AP_startVal = 0;

	for (size_t i = peak.time; i < ADC_counts.size(); i++) {
    //if out of saturation region of preamp and rising for
    //two consecutive samples then we have an after pulse
    if (ADC_counts[i]   < peak.signal*0.9 &&
        ADC_counts[i]   > ADC_counts[i-1] &&
        ADC_counts[i-1] > ADC_counts[i-2] &&
        !APflag)
    {
          APflag = true;
          APmax = ADC_counts[i];
          AP_startVal = ADC_counts[i-2];
          after_pulse.signal = APmax - AP_startVal;
          after_pulse.time = i;
    }
    //if next sample still rising then modify feature signal and time
    if (APflag && ADC_counts[i]>APmax){
      APmax=ADC_counts[i];
      after_pulse.signal = APmax - AP_startVal;
      after_pulse.time = i;
    }

	}

	return after_pulse;
}
