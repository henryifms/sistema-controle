import socket
import ctypes
from ctypes import wintypes
import os

IP_DO_SERVIDOR = ''
PORTA = 5000

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