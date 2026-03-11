#include <windows.h>
#include "keyboard.h"

HHOOK hook;

LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam)
{
    return 1;
}

void lockKeyboard()
{
    hook = SetWindowsHookEx(
        WH_KEYBOARD_LL,
        KeyboardProc,
        NULL,
        0
    );
}

void unlockKeyboard()
{
    UnhookWindowsHookEx(hook);
}
