#ifndef REGULATOR_H
#define REGULATOR_H

#include "mbed.h"

class Regulator {
private:
    AnalogIn AdcVoltageIn;
    AnalogIn AdcCurrentIn;
    AnalogIn AdcVoltageOut;
    AnalogIn AdcCurrentOut;
    uint32_t Frequency;
    double VoltageReference;
    double RealDuty[3] = {0.0};
    double VoltageDifference[3] = {0.0};
    double DigitalVoltageIn = 0.0;
    double DigitalCurrentIn = 0.0;
    double DigitalVoltageOut[3] = {0.0};
    double DigitalCurrentOut = 0.0;
    void sys_init();
    void uart_init();
    void epwm_init();

public:
    Regulator();
    void stage_one_init();
    void stage_two_init();
    void regulate_voltage();
    void change_frequency(uint32_t target);
    void change_duty(double target);
    void commit_changes();
    uint32_t get_frequency();
    double get_duty();
    double voltage_in();
    double current_in();
    double voltage_out();
    double current_out();
    ~Regulator();
};

#endif
