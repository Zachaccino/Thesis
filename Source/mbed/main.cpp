#include "mbed.h"
#include "KVStore.h"
#include "kvstore_global_api.h"
#include "http_request.h"
#include <string>
#define KEY_LENGTH 32
#define VALUE_LENGTH 64


AnalogIn DigitalVoltageIn(A0);       //  Set A0 for ADC of input voltage
AnalogIn DigitalCurrentIn(A1);       //  Set A1 for ADC of input current
AnalogIn DigitalVoltageOut(A2);      //  Set A2 for ADC of output voltage
AnalogIn DigitalCurrentOut(A3);      //  Set A3 for ADC of output current
NetworkInterface *iface;
std::string address = "3.24.141.26:8000";
float Vref = 3.06; 

float RealVoltageIn = 0.0;      //  Input voltage
float RealCurrentIn = 0.0;      //  Input current
float RealVoltageOut = 0.0;     //  Output voltage
float RealCurrentOut = 0.0;     //  Output current
float PowerIn = 0.0;            //  Input power
float PowerOut = 0.0;           //  Output power
float Efficiency = 0.0;         //  Total efficiency
int Index = 0;                  //  Counter index
int DisplayRate = 10000;        //  Display results every 0.1 second
int n = 1;                      //  Average calculation counter
float AVGVoltageIn = 0.0;       //  Average input voltage
float AVGCurrentIn = 0.0;       //  Average input current
float AVGVoltageOut = 0.0;      //  Average output voltage
float AVGCurrentOut = 0.0;      //  Average output current


std::string id() {
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

void set_id(std::string id) {
  char key[KEY_LENGTH] = {"uid"};
  char value[VALUE_LENGTH];
  memset(value, 0, VALUE_LENGTH);
  strcpy(value, id.c_str());
  kv_set(key, value, strlen(value), 0);
}

bool init() {
    iface = NetworkInterface::get_default_instance();
    return iface ? true : false;
}

bool connect() {
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

pair<int, ::string> send(std::string json, http_method method,
                                       std::string endpoint) {
    HttpRequest request = HttpRequest(iface, method, endpoint.c_str());
    request.set_header("Content-Type", "application/json");
    HttpResponse *response = request.send(json.c_str(), strlen(json.c_str()));
    pair<int, std::string> result =
        make_pair(response->get_status_code(), response->get_body_as_string());
    delete response;
    return result;
}

void deinit() {
  iface->disconnect();
  delete iface;
  iface = NULL;
}

pair<int, std::string> register_device(std::string id) {
  string json = "{\"device_id\": \"" + id + "\"}";
  return send(json, HTTP_POST, "http://" + address + "/register_device");
}

pair<int, std::string> add_telemetry(std::string id, float v_out, float c_out, float v_in, float c_in) {
  string json = "{\"device_id\": \"" + id +
                "\",\"voltage_in\":" + to_string(v_in) +
                ",\"current_in\":" + to_string(c_in) + 
                ",\"voltage_out\":" + to_string(v_out) + 
                ",\"current_out\":" + to_string(c_out) + 
                "}";
  return send(json, HTTP_POST, "http://" + address + "/add_telemetry");
}


int main() {
    printf("Started.\n");

    // Setup and connect to Wi-fi or Cellular network.
    init();
    connect();
    printf("Connected.\n");

    // Configure device.
    pair<int, std::string> response = register_device(id());

    if (response.first == 200) {
        set_id(response.second);
        printf("Device registration completed. Device ID is: %s\n", response.second.c_str());
    } else {
        deinit();
        printf("Device registration failed.\n");
        return 1;
    }
    
    while (true) {
        RealVoltageIn = 11 * DigitalVoltageIn.read() * Vref;   //  Voltage divider 10:1
        RealCurrentIn   =   -(4.9031 * DigitalCurrentIn.read() * Vref * 3 / 2 - 12.414);    //  Input current using 10A sensor, voltage divider 1:2 applied, why negative?
        RealVoltageOut  =   11 * DigitalVoltageOut.read() * Vref;    //  Voltage divider 10:1
        RealCurrentOut  =   -10 * DigitalCurrentOut.read() * Vref +25;   //  Output current using new sensor, why negative?
        Index++;
        
        if(Index == DisplayRate/5*n){
            AVGVoltageIn = (AVGVoltageIn * (n-1) + RealVoltageIn)/n;    // Get average input voltage
            AVGCurrentIn = (AVGCurrentIn * (n-1) + RealCurrentIn)/n;    // Get average input current
            AVGVoltageOut = (AVGVoltageOut * (n-1) + RealVoltageOut)/n; // Get average output voltage
            AVGCurrentOut = (AVGCurrentOut * (n-1) + RealCurrentOut)/n; // Get average output current
            n++;
        }

        if(Index >= DisplayRate){
            Index = 0;
            n = 1;
            
            /* Clear negative values */
            if(AVGVoltageIn < 0){
                AVGVoltageIn = 0.0;
            }
            if(AVGCurrentIn < 0){
                AVGCurrentIn = 0.0;
            }
            if(AVGVoltageOut < 0){
                AVGVoltageOut = 0.0;
            }
            if(AVGCurrentOut < 0){
                AVGCurrentOut = 0.0;
            }
            
            /* Set the initial value of the current sensors to 0  */
            if(AVGCurrentIn <= 12.414000 && AVGCurrentIn >= 12.4139){
                AVGCurrentIn = 0.0;
                AVGCurrentOut = 0.0;
            }
            PowerIn  = AVGVoltageIn * AVGCurrentIn;    //  Pin = Vin * Iin
            PowerOut = AVGVoltageOut * AVGCurrentOut; //  Pout = Vout * Iout
            Efficiency = PowerOut / PowerIn * 100;  //  Efficiency in percent

            string json = "{\"device_id\": \"" + id() +
                "\",\"voltage_in\":" + to_string(AVGVoltageIn) +
                ",\"current_in\":" + to_string(AVGCurrentIn) + 
                ",\"voltage_out\":" + to_string(AVGVoltageOut) + 
                ",\"current_out\":" + to_string(AVGCurrentOut) + 
                "}";
            HttpRequest request = HttpRequest(iface, HTTP_POST, ("http://" + address + "/add_telemetry").c_str());
            request.set_header("Content-Type", "application/json");
            HttpResponse *response = request.send(json.c_str(), strlen(json.c_str()));
            printf("Sent\n");
            printf("%s\n", json.c_str());
            printf("%d\n", response->get_status_code());
            
            /* Clear the average values */
            AVGVoltageIn = 0.0;
            AVGCurrentIn = 0.0;
            AVGVoltageOut = 0.0;
            AVGCurrentOut = 0.0;
        }

        wait_us(10);    //  Sampling rate 10kHz
    }

    // Clean up.
    printf("Cleaning up.\n");
    deinit();
    printf("Shutting down.\n");
    return 0;
}