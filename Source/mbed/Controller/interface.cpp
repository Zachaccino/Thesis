#include "interface.h"

Interface::Interface() : iface(NetworkInterface::get_default_instance()) {}

bool Interface::connect() {
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

pair<int, std::string> Interface::send(std::string json, http_method method,
                                       std::string endpoint) {
  HttpRequest *request = new HttpRequest(iface, method, endpoint.c_str());
  request->set_header("Content-Type", "application/json");
  HttpResponse *response = request->send(json.c_str(), strlen(json.c_str()));

  pair<int, std::string> result =
      make_pair(response->get_status_code(), response->get_body_as_string());

  delete request;
  delete response;

  return result;
}

Interface::~Interface() { delete iface; }