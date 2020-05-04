#include "mbed.h"
#include "http_request.h"
#include "KVStore.h"
#include "kvstore_global_api.h"


// Server Configurations.
const string server_address = "192.168.1.3:5000";
const int max_retry = 3;

// KV Store Configurations.
const int key_length = 32;
const int value_length = 64;

// Setup.
Serial serial(USBTX, USBRX);
NetworkInterface *iface;

// TESTING ONLY.
float voltage = 5.5;
float ampere = 2.0;
bool power = true;
Mutex accessRight;


// Initialise the Network Interface.
bool init() 
{
    serial.printf("Initialisation...\n");

    iface = NetworkInterface::get_default_instance();

    if (!iface) 
    {
        serial.printf("Inteface Initialisation FAILED...\n");
        return false;
    }

    srand(time(NULL));
    return true;
}

// Connect to the Internet.
bool connect() 
{
    serial.printf("Connecting...\n");

    int n_retry = 0;
    bool connected = iface->get_connection_status() == NSAPI_STATUS_GLOBAL_UP;

    while (!connected && n_retry < max_retry) 
    {
        serial.printf("Attempt %d...\n", n_retry);

        iface->connect();
        connected = iface->get_connection_status() == NSAPI_STATUS_GLOBAL_UP;
        n_retry++;
    }

    if (!connected)
    {
        serial.printf("Connection Establishment FAILED...\n");
        return false;
    }

    serial.printf("Connection Established!\n");
    return true;
}

// Send an HTTP Request.
pair<int, string> send(string json, http_method method, string endpoint)
{
    HttpRequest* req = new HttpRequest(iface, method, endpoint.c_str());
    req->set_header("Content-Type", "application/json");
    HttpResponse* response = req->send(json.c_str(), strlen(json.c_str()));

    string content = "";
    int status_code = response->get_status_code();

    if (status_code == 200)
    {
        content = response->get_body_as_string();
    }

    delete req;
    return make_pair(status_code, response->get_body_as_string());
}

// Free Resources.
void deinit()
{
    delete iface;
}

// Utils
string device_uid()
{
    char key[key_length] = {"uid"};
    size_t actual_size = 0;
    kv_info_t kv_info;
    
    kv_get_info(key, &kv_info);
    char value[kv_info.size + 1];
    memset(value, 0, kv_info.size + 1);
    kv_get(key, value, kv_info.size, &actual_size);

    return string(value);
}

// API Calls.
pair<int, string> add_device(string uid, string device)
{   
    string json = "{\"uid\": \"" + uid + "\",\"device\": \"" + device + "\"}";
    return send(json, HTTP_POST, "http://" + server_address + "/add_device");
}

pair<int, string> add_telemetry(string uid, double voltage, double ampere)
{
    string json = "{\"uid\": \"" + uid + "\",\"voltage\":" + to_string(voltage) + ",\"ampere\":" + to_string(ampere) + "}";
    serial.printf("TELEMETRY SENT: %s\n", json.c_str());
    return send(json, HTTP_POST, "http://" + server_address + "/add_telemetry");
}

pair<int, string> pull_events(string uid)
{   
    string json = "{\"uid\": \"" + uid + "\"}";
    return send(json, HTTP_POST, "http://" + server_address + "/pull_events");
}

// Configure Device.
void config()
{
    serial.printf("Configuring Device...\n");
    char key[key_length] = {"uid"};
    kv_info_t kv_info;

    if (kv_get_info(key, &kv_info) != MBED_SUCCESS)
    {
        pair<int, string> res = add_device("", "NUMAKER_M263A");
        char value[value_length];
        memset(value, 0, value_length);
        strcpy(value, res.second.c_str());
        kv_set(key, value, strlen(value), 0);
    } else 
    {
        add_device(device_uid(), "NUMAKER_M263A");
    }
    
    return;
}


// Debug Purposes
double rand_offset()
{
    double f = (double)rand() / RAND_MAX;
    return -1 + f * (1 + 1);
}


// Thread Workers
void executor()
{   
    string* raw_cmd = NULL;
    string* cmd_code = NULL;
    string* cmd_value = NULL;
    bool contine = true;

    while (contine) {
        pair<int, string> res = pull_events(device_uid());

        raw_cmd = new string(res.second);
        string delim = ",";

        size_t code_pos = raw_cmd->find(delim);
        cmd_code = new string(raw_cmd->substr(0, code_pos));

        raw_cmd->erase(0, code_pos + delim.length());

        size_t value_pos = raw_cmd->find(delim);
        cmd_value = new string(raw_cmd->substr(0, value_pos));
        
        if (*cmd_code == "setVoltage")
        {
            voltage = stod(*cmd_value);
        } 
        else if (*cmd_code == "setAmpere")
        {
            ampere = stod(*cmd_value);
        }
        else if (*cmd_code == "powerDown")
        {
            power = false;
            contine = false;
        }
        else {
            contine = false;
        }

        delete raw_cmd;
        delete cmd_code;
        delete cmd_value;
    }
}

void monitor()
{
    add_telemetry(device_uid(), voltage + rand_offset(), ampere + rand_offset());
}


int main()
{
    if (!init())
    {
        return 0 ;
    }

    if (!connect())
    {
        deinit();
        return 0 ;
    }

    config();
    serial.printf("This Device ID is: %s\n", device_uid().c_str());

    
    while (power)
    {
        monitor();
        executor();
        ThisThread::sleep_for(1000);
    }

    deinit();

    serial.printf("Program Terminated\n\n\n");
    return 0;
}

