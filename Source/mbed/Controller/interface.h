#ifndef INTERFACE_H
#define INTERFACE_H

#include "http_request.h"
#include "mbed.h"
#include <string>

class Interface {
private:
  NetworkInterface *iface;

public:
  Interface();
  bool connect();
  pair<int, std::string> send(std::string json, http_method method,
                              std::string endpoint);
  ~Interface();
};

#endif