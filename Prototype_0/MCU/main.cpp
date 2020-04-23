#include "mbed.h"
#include "http_request.h"


// Configurations.
const char *server_address = "httpbin.org";
const int server_port = 80;
const int max_retry = 3;


// Setup.
Serial serial(USBTX, USBRX);
NetworkInterface *iface;
TCPSocket* sock;


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

    sock = new TCPSocket();

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

    if (sock->open(iface) != NSAPI_ERROR_OK) 
    {
        serial.printf("Socket Opening FAILED...\n");
        return false;
    }

    SocketAddress addr;

    if (iface->gethostbyname(server_address, &addr) != NSAPI_ERROR_OK)
    {
        serial.printf("Host Address Acquirement FAILED...\n");
        return false;
    }

    addr.set_port(server_port);
    sock->set_timeout(15000);

    if (sock->connect(addr) < 0)
    {
        serial.printf("Socket Establishment FAILED...\n");
        return false;
    }

    serial.printf("Connection Established!\n");
    return true;
}

// Send an HTTP Request.
pair<int, string> send(const char* json, http_method method, const char* endpoint)
{
    HttpRequest* req = new HttpRequest(sock, method, endpoint);
    req->set_header("Content-Type", "application/json");
    HttpResponse* response = req->send(json, strlen(json));

    string content = "";
    int status_code = response->get_status_code();

    if (status_code == 200)
    {
        content = response->get_body_as_string();
    }

    delete req;
    return make_pair(status_code, response->get_body_as_string());
}

void deinit()
{
    delete iface;
    delete sock;
}

int main()
{
    if (!init())
    {
        return 0;
    }

    if (!connect())
    {
        deinit();
        return 0;
    }

    pair<int, string> res = send("{\"hello\":\"world\"}", HTTP_GET, "http://httpbin.org/status/418");

    serial.printf("%d\n", res.first);
    serial.printf("%s\n", res.second.c_str());

    // if (res.first != 200)
    // {
    //     serial.printf("GET REQUEST FAILED.\n");
    // }
    // else
    // {
    //     serial.printf("%s\n", res.second.c_str());
    // }

    deinit();
    return 0;
}

