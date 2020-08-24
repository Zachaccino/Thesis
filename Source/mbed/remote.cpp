#include "remote.h"

Remote::Remote(std::string address) : iface(NULL), address(address) {}

bool Remote::init() {
    iface = NetworkInterface::get_default_instance();
    return iface ? true : false;
}

bool Remote::connect() {
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

pair<int, ::string> Remote::send(std::string json, http_method method,
                                       std::string endpoint) {
  HttpRequest request = HttpRequest(iface, method, endpoint.c_str());
  request.set_header("Content-Type", "application/json");
  HttpResponse *response = request.send(json.c_str(), strlen(json.c_str()));

  pair<int, std::string> result =
      make_pair(response->get_status_code(), response->get_body_as_string());

  delete response;
  return result;
}

void Remote::deinit() {
  iface->disconnect();
  delete iface;
  iface = NULL;
}

pair<int, std::string> Remote::register_device(std::string id) {
  string json = "{\"device_id\": \"" + id + "\"}";
  return send(json, HTTP_POST, "http://" + address + "/register_device");
}

pair<int, std::string> Remote::add_telemetry(std::string id, double voltage,
                                             double current) {
  string json = "{\"device_id\": \"" + id +
                "\",\"voltage\":" + to_string(voltage) +
                ",\"current\":" + to_string(current) + "}";
  return send(json, HTTP_POST, "http://" + address + "/add_telemetry");
}

Remote::~Remote() {}
