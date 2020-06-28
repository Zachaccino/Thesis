#include "remote.h"

Remote::Remote(Interface *iface, std::string address)
    : iface(iface), address(address) {}

pair<int, std::string> Remote::add_device(std::string id) {
  string json = "{\"device_id\": \"" + id + "\"}";
  return iface->send(json, HTTP_POST, "http://" + address + "/add_device");
}

pair<int, std::string> Remote::add_telemetry(std::string id, double voltage,
                                             double ampere) {
  string json = "{\"device_id\": \"" + id +
                "\",\"voltage\":" + to_string(voltage) +
                ",\"ampere\":" + to_string(ampere) + "}";
  return iface->send(json, HTTP_POST, "http://" + address + "/add_telemetry");
}

pair<int, std::string> Remote::pull_events(std::string id) {
  string json = "{\"device_id\": \"" + id + "\"}";
  return iface->send(json, HTTP_POST, "http://" + address + "/pull_event");
}

Remote::~Remote() {}
