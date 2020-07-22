#ifndef REMOTE_H
#define REMOTE_H

#include "http_request.h"
#include "interface.h"
#include <string>

class Remote {
private:
  Interface *iface;
  std::string address;

public:
  Remote(Interface *iface, std::string address);
  pair<int, std::string> add_device(std::string id);
  pair<int, std::string> add_telemetry(std::string id, double voltage,
                                       double ampere);
  pair<int, std::string> pull_events(std::string id);
  ~Remote();
};

#endif