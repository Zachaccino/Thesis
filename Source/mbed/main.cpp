#include "info.h"
#include "mbed.h"
#include "remote.h"

Info info = Info();
Remote remote = Remote("192.168.1.14:8000");
Serial serial(USBTX, USBRX);
Mutex serialMutex;

// Just send telemetry and pull events.
void executor() {
    // Sending telemetry.
    remote.add_telemetry(info.id(), 13.14, 11.9);

    // Receiving event.
    pair<int, std::string> response = remote.pull_event(info.id());
    string json = response.second;
    string e = "";
    size_t pos = 0;
    int count = 0;

    while ((pos = json.find(",")) != std::string::npos) {
        if (count % 2 == 0) {
            e = json.substr(0, pos);
            json.erase(0, pos + 1);
        } else {
            string v = json.substr(0, pos);
            json.erase(0, pos + 1);
            serial.printf("%s : %s\n", e.c_str(), v.c_str());
        }
        count++;
    }
}

int main() {
    serial.printf("Started.\n");

    // Setup and connect to Wi-fi or Cellular network.
    remote.init();
    remote.connect();
    serial.printf("Connected.\n");

    // Configure device.
    pair<int, std::string> response = remote.register_device(info.id());

    if (response.first == 200) {
        info.set_id(response.second);
        serial.printf("Device registration completed. Device ID is: %s\n", response.second.c_str());
    } else {
        remote.deinit();
        serial.printf("Device registration failed.\n");
        return 0;
    }

    // Clean up.
    remote.deinit();
    serial.printf("Shutting down.\n");
    return 0;
}