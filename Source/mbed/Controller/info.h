#ifndef INFO_H
#define INFO_H

#include "KVStore.h"
#include "kvstore_global_api.h"
#include <string>

class Info {
public:
  Info();
  std::string id();
  void set_id(std::string id);
  ~Info();
};

#endif