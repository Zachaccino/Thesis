#ifndef REMOTE_H
#define REMOTE_H

#include "http_request.h"
#include "mbed.h"
#include <string>

class Remote {
private:
  NetworkInterface *iface;
  std::string address;
  pair<int, std::string> send(std::string json, http_method method,
                              std::string endpoint);

public:
  Remote(std::string address);
  ~Remote();
  
  // Interface Utilities.
  bool init();
  bool connect();
  void deinit();

  // API End Points.
  pair<int, std::string> register_device(std::string id);
  pair<int, std::string> add_telemetry(std::string id, double voltage,
                                       double ampere);
};

#endif