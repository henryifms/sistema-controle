#include "network.h"
#include <winsock2.h>

#pragma comment(lib,"ws2_32.lib")

Command waitCommand()
{
    static bool initialized = false;
    static SOCKET sock;

    if(!initialized)
    {
        WSADATA wsa;
        WSAStartup(MAKEWORD(2,2), &wsa);

        sock = socket(AF_INET, SOCK_DGRAM, 0);

        sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(5000);
        addr.sin_addr.s_addr = INADDR_ANY;

        bind(sock,(sockaddr*)&addr,sizeof(addr));

        initialized = true;
    }

    Command cmd;
    recv(sock,(char*)&cmd,sizeof(cmd),0);

    return cmd;
}
