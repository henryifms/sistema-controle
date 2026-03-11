#include "network.h"
#include "keyboard.h"
#include "../shared/protocol.h"

int main()
{
    while(true)
    {
        Command cmd = waitCommand();

        if(cmd == CMD_LOCK)
            lockKeyboard();

        if(cmd == CMD_UNLOCK)
            unlockKeyboard();
    }
}
