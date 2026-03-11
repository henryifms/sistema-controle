#include "network.h"
#include "../shared/protocol.h"
#include <iostream>

int main()
{
    char input;

    while(true)
    {
        std::cout << "L = lock, U = unlock\n";
        std::cin >> input;

        if(input == 'L')
            broadcastCommand(CMD_LOCK);

        if(input == 'U')
            broadcastCommand(CMD_UNLOCK);
    }
}
