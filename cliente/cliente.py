import socket
import ctypes
from ctypes import wintypes
import os
import time

IP_DO_SERVIDOR = '10.8.33.xxx'
PORTA = 5000

keybd_event = ctypes.windll.user32.keybd_event
VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002

BlockInput = ctypes.windll.user32.BlockInput
BlockInput.argtypes = [wintypes.BOOL]
BlockInput.restype = wintypes.BOOL

def travar_teclado():
    if BlockInput(True):
        print("Teclado e mouse BLOQUEADOS")
    else:
        print("Erro ao bloquear (rode como ADMIn)")

def destravar_teclado():
    if BlockInput(False):
        print("Teclado e mouse DESBLOQUEADOS")
    else:
        print("Erro ao desbloquear")

def pressionar_enter_2x():
    for _ in range(2):
        keybd_event(VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)

# Configuração do socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((IP_DO_SERVIDOR, PORTA))
    print("Conectado ao servidor!")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit()

while True:
    try:
        dados = client.recv(1024)
        if not dados:
            break
        
        mensagem = dados.decode().strip()
        print(f"COMANDO RECEBIDO: {mensagem}")

        match mensagem:
            case "BLOQUEAR_TECLADO":
                travar_teclado()
            case "DESBLOQUEAR_TECLADO":
                destravar_teclado()
            case "BLOQUEAR_TELA":
                print("Bloqueando tela...")
                os.system("rundll32.exe user32.dll,LockWorkStation")
                travar_teclado()
            case "DESBLOQUEAR_TELA":
                print("Tentando preparar tela de login...")
                destravar_teclado()
                time.sleep(1)
                pressionar_enter_2x()
            case _:
                print("Comando dsconhecido.")
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        break

client.close()
