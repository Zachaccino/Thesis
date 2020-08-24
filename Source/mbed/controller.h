#ifndef CONTROLLER_H
#define CONTROLLER_H

#include "KVStore.h"
#include "kvstore_global_api.h"
#include <string>

class Controller {
public:
  Controller();
  std::string id();
  void set_id(std::string id);
  ~Controller();
};

#endif