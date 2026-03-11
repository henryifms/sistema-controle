#include "network.h"
#include <winsock2.h>

#pragma comment(lib,"ws2_32.lib")

void broadcastCommand(Command cmd)
{
    WSADATA wsa;
    WSAStartup(MAKEWORD(2,2), &wsa);

    SOCKET sock = socket(AF_INET, SOCK_DGRAM, 0);

    int broadcast = 1;
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, (char*)&broadcast, sizeof(broadcast));

    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(5000);
    addr.sin_addr.s_addr = INADDR_BROADCAST;

    sendto(sock,(char*)&cmd,sizeof(cmd),0,(sockaddr*)&addr,sizeof(addr));
}
