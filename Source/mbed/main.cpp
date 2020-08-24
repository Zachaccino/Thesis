#include "controller.h"
#include "mbed.h"
#include "remote.h"
#include "regulator.h"


Thread thread;
double voltage_out;
double current_out;


// void monitor() {
//     printf("Started.\n");

//     Controller device = Controller();
//     Remote remote = Remote("192.168.1.14:8000");

//     // Setup and connect to Wi-fi or Cellular network.
//     remote.init();
//     remote.connect();
//     printf("Connected.\n");

//     // Configure device.
//     pair<int, std::string> response = remote.register_device(device.id());

//     if (response.first == 200) {
//         device.set_id(response.second);
//         printf("Device registration completed. Device ID is: %s\n", response.second.c_str());
//     } else {
//         remote.deinit();
//         printf("Device registration failed.\n");
//         return;
//     }
    
//     while (true) {
//         printf("Monitoring...\n");
//         // Sending telemetries and receiving event.
//         pair<int, std::string> response = remote.add_telemetry(device.id(), voltage_out, current_out);
//         string csv = response.second;
//         string e = "";
//         size_t pos = 0;
//         int count = 0;
//         printf("Decrypting...\n");

//         while ((pos = csv.find(",")) != std::string::npos) {
//             printf("Interpreting...\n");
//             if (count % 2 == 0) {
//                 e = csv.substr(0, pos);
//                 csv.erase(0, pos + 1);
//             } else {
//                 string v = csv.substr(0, pos);
//                 csv.erase(0, pos + 1);
//                 printf("%s : %s\n", e.c_str(), v.c_str());
//             }
//             count++;
//         }
//         printf("Sleeping...\n");
//         ThisThread::sleep_for(1000);
//         printf("SleepingDone...\n");
//     }

//     // Clean up.
//     printf("Cleaning up.\n");
//     remote.deinit();
//     printf("Shutting down.\n");
// }


int main() {
    //thread.start(monitor);

    Regulator regulator = Regulator();

    // Init.
    regulator.stage_one_init();
    regulator.stage_two_init();
    printf("Initialised...\n");

    // Set starting power targets.
    regulator.change_frequency(100000);
    regulator.change_duty(0.4);
    regulator.commit_changes();
    printf("Initial Power Target is Set...\n");

    // Change state every 5 seconds.
    int cycles = 0;
    int max_cycles = 50;
    double delta_freq = 5000;
    double delta_duty = 0.2;

    // Testing if it can change duty and frequency on the fly.
    while (true) {
        // Either increase or decrease the frequency and duty after 50 cycles. (or 5 seconds)
        if (cycles >= max_cycles) {
            cycles = 0;
            regulator.change_frequency(100000 + delta_freq);
            regulator.change_duty(0.4 + delta_duty);
            regulator.commit_changes();
            delta_duty *= -1;
            delta_freq *= -1;
        }
        regulator.regulate_voltage();
        voltage_out = regulator.voltage_out();
        current_out = regulator.current_out();
        wait_us(100);
        cycles++;
    }

    return 0;
}