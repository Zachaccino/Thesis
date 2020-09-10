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
    printf("10.1\n");
    HttpRequest request = HttpRequest(iface, method, endpoint.c_str());
    printf("10.2\n");
    request.set_header("Content-Type", "application/json");
    printf("10.3\n");
    HttpResponse *response = request.send(json.c_str(), strlen(json.c_str()));
    printf("10.4\n");
    pair<int, std::string> result =
        make_pair(response->get_status_code(), response->get_body_as_string());
    printf("10.5\n");
    delete response;
    printf("10.6\n");
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

pair<int, std::string> Remote::add_telemetry(std::string id, float v_out, float c_out, float v_in, float c_in) {
  string json = "{\"device_id\": \"" + id +
                "\",\"voltage_in\":" + to_string(v_in) +
                ",\"current_in\":" + to_string(c_in) + 
                ",\"voltage_out\":" + to_string(v_out) + 
                ",\"current_out\":" + to_string(c_out) + 
                "}";
  return send(json, HTTP_POST, "http://" + address + "/add_telemetry");
}

Remote::~Remote() {}
