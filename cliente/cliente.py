import socket
import ctypes
from ctypes import wintypes
import os
import time

IP_DO_SERVIDOR = '10.8.33.158'
PORTA = 5000

keybd_event = ctypes.windll.user32.keybd_event

VK_RETURN = 0x0D  # código da tecla ENTER
KEYEVENTF_KEYUP = 0x0002

BlockInput = ctypes.windll.user32.BlockInput
BlockInput.argtypes = [wintypes.BOOL]
BlockInput.restype = wintypes.BOOL

def travar_teclado():
    ok = BlockInput(True)
    if ok:
        print("Teclado e mouse BLOQUEADOS")
    else:
        print("Erro ao bloquear (rode como ADMIn)")

def destravar_teclado():
    ok = BlockInput(False)
    if ok:
        print("Teclado e mouse DESBLOQUEADOS")
    else:
        print("Erro ao desbloquear")

def pressionar_enter_2x():
    for _ in range(2):
        keybd_event(VK_RETURN, 0, 0, 0)  # tecla down
        time.sleep(0.05)
        keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)  # tecla up
        time.sleep(0.2)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP_DO_SERVIDOR, PORTA))

print("Conectado ao servidor!")

while True:
    mensagem = client.recv(1024).decode().strip()
    
    if mensagem:
        print(f"COMANDO RECEBIDO: {mensagem}")

        if mensagem == "BLOQUEAR_TECLADO":
            travar_teclado()

        elif mensagem == "DESBLOQUEAR_TECLADO":
            destravar_teclado()

        elif mensagem == "BLOQUEAR_TELA":
            print("Bloqueando tela...")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            travar_teclado()

        elif mensagem == "DESBLOQUEAR_TELA":
            print("Windows não permite destravar tela por scipt (segurança)")
            destravar_teclado()
            time.sleep(1)
            pressionar_enter_2x()