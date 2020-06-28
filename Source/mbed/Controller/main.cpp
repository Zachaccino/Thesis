#include "info.h"
#include "interface.h"
#include "mbed.h"
#include "remote.h"


// // Setup.
// Serial serial(USBTX, USBRX);

// // TESTING ONLY.
// float voltage = 5.5;
// float ampere = 2.0;
// bool power = true;
// Mutex accessRight;

// // Debug Purposes
// double rand_offset() {
//   double f = (double)rand() / RAND_MAX;
//   return -1 + f * (1 + 1);
// }

// // Thread Workers
// void executor() {
//   string *raw_cmd = NULL;
//   string *cmd_code = NULL;
//   string *cmd_value = NULL;
//   bool contine = true;

//   while (contine) {
//     pair<int, string> res = pull_events(device_uid());

//     raw_cmd = new string(res.second);
//     string delim = ",";

//     size_t code_pos = raw_cmd->find(delim);
//     cmd_code = new string(raw_cmd->substr(0, code_pos));

//     raw_cmd->erase(0, code_pos + delim.length());

//     size_t value_pos = raw_cmd->find(delim);
//     cmd_value = new string(raw_cmd->substr(0, value_pos));

//     if (*cmd_code == "setVoltage") {
//       voltage = stod(*cmd_value);
//     } else if (*cmd_code == "setAmpere") {
//       ampere = stod(*cmd_value);
//     } else if (*cmd_code == "powerDown") {
//       power = false;
//       contine = false;
//     } else {
//       contine = false;
//     }

//     delete raw_cmd;
//     delete cmd_code;
//     delete cmd_value;
//   }
// }

// void monitor() {
//   add_telemetry(device_uid(), voltage + rand_offset(), ampere + rand_offset());
// }

int main() {
//   if (!init()) {
//     return 0;
//   }

//   if (!connect()) {
//     deinit();
//     return 0;
//   }

//   config();
//   serial.printf("This Device ID is: %s\n", device_uid().c_str());

//   while (power) {
//     monitor();
//     executor();
//     ThisThread::sleep_for(1000);
//   }

//   deinit();

//   serial.printf("Program Terminated\n\n\n");
  return 0;
}
