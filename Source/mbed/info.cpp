#include "info.h"

#define KEY_LENGTH 32
#define VALUE_LENGTH 64
#include "mbed.h"
#include "NuMicro.h"

Info::Info() {}

std::string Info::id() {
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

void Info::set_id(std::string id) {
  char key[KEY_LENGTH] = {"uid"};
  char value[VALUE_LENGTH];
  memset(value, 0, VALUE_LENGTH);
  strcpy(value, id.c_str());
  kv_set(key, value, strlen(value), 0);
}

Info::~Info() {}