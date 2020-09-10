#ifndef REGULATOR_H
#define REGULATOR_H

#include "mbed.h"

class Regulator {
private:
    AnalogIn voltageOutPin;     //  Set A0 for ADC of output voltage
    AnalogIn currentOutPin;     //  Set A1 for ADC of output current
    AnalogIn voltageInPin;      //  Set A2 for ADC of input voltage
    AnalogIn currentInPin;      //  Set A3 for ADC of input current

public:
    Regulator();
    float v_in();
    float c_in();
    float v_out();
    float c_out();
    ~Regulator();
};

#endif
