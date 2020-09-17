#include "mbed.h"
#include "KVStore.h"
#include "kvstore_global_api.h"
#include "http_request.h"
#include <string>
#define KEY_LENGTH 32
#define VALUE_LENGTH 64


AnalogIn voltageOutPin(A0);
AnalogIn currentOutPin(A1);
AnalogIn voltageInPin(A2);
AnalogIn currentInPin(A3);
NetworkInterface *iface;
std::string address = "3.24.141.26:8000";


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

float v_out() {
    return 11*voltageInPin.read()*3.3f;
}

float c_out() {
    return -13.515 * currentInPin.read()*3.3f + 38.859;
}

float v_in() {
    return 11*voltageOutPin.read()*3.3f;
}

float c_in() {
    return -5 * currentOutPin.read() * 3.3f + 12.665;
}

bool init() {
    iface = NetworkInterface::get_default_instance();
    return iface ? true : false;
}

bool connect() {
  int n_retry = 0;
  int max_retry = 3;
  bool connected = iface->get_connection_status() == NSAPI_STATUS_GLOBAL_UP;

  while (!connected && n_retry < max_retry) {
    iface->connect();
    connected = iface->get_connection_status() == NSAPI_STATUS_GLOBAL_UP;
    n_retry++;
  }

  return connected;
}

pair<int, ::string> send(std::string json, http_method method,
                                       std::string endpoint) {
    HttpRequest request = HttpRequest(iface, method, endpoint.c_str());
    request.set_header("Content-Type", "application/json");
    HttpResponse *response = request.send(json.c_str(), strlen(json.c_str()));
    pair<int, std::string> result =
        make_pair(response->get_status_code(), response->get_body_as_string());
    delete response;
    return result;
}

void deinit() {
  iface->disconnect();
  delete iface;
  iface = NULL;
}

pair<int, std::string> register_device(std::string id) {
  string json = "{\"device_id\": \"" + id + "\"}";
  return send(json, HTTP_POST, "http://" + address + "/register_device");
}

pair<int, std::string> add_telemetry(std::string id, float v_out, float c_out, float v_in, float c_in) {
  string json = "{\"device_id\": \"" + id +
                "\",\"voltage_in\":" + to_string(v_in) +
                ",\"current_in\":" + to_string(c_in) + 
                ",\"voltage_out\":" + to_string(v_out) + 
                ",\"current_out\":" + to_string(c_out) + 
                "}";
  return send(json, HTTP_POST, "http://" + address + "/add_telemetry");
}


int main() {
    printf("Started.\n");

    // Setup and connect to Wi-fi or Cellular network.
    init();
    connect();
    printf("Connected.\n");

    // Configure device.
    pair<int, std::string> response = register_device(id());

    if (response.first == 200) {
        set_id(response.second);
        printf("Device registration completed. Device ID is: %s\n", response.second.c_str());
    } else {
        deinit();
        printf("Device registration failed.\n");
        return 1;
    }
    
    while (true) {
        // Sending telemetries and receiving event.
        string json = "{\"device_id\": \"" + id() +
                "\",\"voltage_in\":" + to_string(v_in()) +
                ",\"current_in\":" + to_string(c_in()) + 
                ",\"voltage_out\":" + to_string(v_out()) + 
                ",\"current_out\":" + to_string(c_out()) + 
                "}";
        HttpRequest request = HttpRequest(iface, HTTP_POST, ("http://" + address + "/add_telemetry").c_str());
        request.set_header("Content-Type", "application/json");
        HttpResponse *response = request.send(json.c_str(), strlen(json.c_str()));
        printf("Sent\n");
        printf("%s\n", json.c_str());
        printf("%d\n", response->get_status_code());
        // pair<int, std::string> result = make_pair(response->get_status_code(), response->get_body_as_string());
        // string csv = result.second;
        // string e = "";
        // size_t pos = 0;
        // int count = 0;
        // while ((pos = csv.find(",")) != std::string::npos) {
        //     if (count % 2 == 0) {
        //         e = csv.substr(0, pos);
        //         csv.erase(0, pos + 1);
        //     } else {
        //         string v = csv.substr(0, pos);
        //         csv.erase(0, pos + 1);
        //          printf("%s : %s\n", e.c_str(), v.c_str());
        //     }
        //     count++;
        // }
        ThisThread::sleep_for(1000);
    }

    // Clean up.
    printf("Cleaning up.\n");
    deinit();
    printf("Shutting down.\n");
    return 0;
}