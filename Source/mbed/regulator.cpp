#include "regulator.h"

Regulator::Regulator()
    : voltageOutPin(A0), currentOutPin(A1), voltageInPin(A2), currentInPin(A3) {
}

float Regulator::v_out() {
    return 11*voltageInPin.read()*3.3f;
}

float Regulator::c_out() {
    return -13.515 * currentInPin.read()*3.3f + 38.859;
}

float Regulator::v_in() {
    return 11*voltageOutPin.read()*3.3f;
}

float Regulator::c_in() {
    return -5 * currentOutPin.read() * 3.3f + 12.665;
}

Regulator::~Regulator() {}
