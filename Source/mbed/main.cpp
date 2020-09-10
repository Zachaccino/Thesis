#include "mbed.h"
#include "controller.h"
#include "remote.h"
#include "regulator.h"
#include "KVStore.h"
#include "kvstore_global_api.h"
#include <string>
#define KEY_LENGTH 32
#define VALUE_LENGTH 64


std::string id() {
  char key[KEY_LENGTH] = {"uid"};
  kv_info_t kv_info;

  if (kv_get_info(key, &kv_info) == MBED_SUCCESS) {
    char value[kv_info.size + 1];
    memset(value, 0, kv_info.size + 1);
    size_t actual_size = 0;
    kv_get(key, value, kv_info.size, &actual_size);
    return std::string(value);
  }

  return "";
}

void set_id(std::string id) {
  char key[KEY_LENGTH] = {"uid"};
  char value[VALUE_LENGTH];
  memset(value, 0, VALUE_LENGTH);
  strcpy(value, id.c_str());
  kv_set(key, value, strlen(value), 0);
}


int main() {
    printf("Started.\n");

    Controller device = Controller();
    Remote remote = Remote("3.24.141.26:8000");
    Regulator regulator = Regulator();

    // Setup and connect to Wi-fi or Cellular network.
    remote.init();
    remote.connect();
    printf("Connected.\n");

    // Configure device.
    pair<int, std::string> response = remote.register_device(device.id());

    if (response.first == 200) {
        device.set_id(response.second);
        printf("Device registration completed. Device ID is: %s\n", response.second.c_str());
    } else {
        remote.deinit();
        printf("Device registration failed.\n");
        return 1;
    }
    
    while (true) {
        printf("1.\n");
        // Sending telemetries and receiving event.
        pair<int, std::string> response = remote.add_telemetry(device.id(), regulator.v_out(), regulator.c_out(), regulator.v_in(), regulator.c_in());
        printf("2.\n");
        string csv = response.second;
        string e = "";
        size_t pos = 0;
        int count = 0;
        printf("3.\n");
        while ((pos = csv.find(",")) != std::string::npos) {
            if (count % 2 == 0) {
                e = csv.substr(0, pos);
                csv.erase(0, pos + 1);
            } else {
                string v = csv.substr(0, pos);
                csv.erase(0, pos + 1);
                 printf("%s : %s\n", e.c_str(), v.c_str());
            }
            count++;
        }
        printf("4.\n");
        ThisThread::sleep_for(1000);
        printf("5.\n");
    }

    // Clean up.
    printf("Cleaning up.\n");
    remote.deinit();
    printf("Shutting down.\n");
    return 0;
}