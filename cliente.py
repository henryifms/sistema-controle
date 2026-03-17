import requests
import time
import keyboard

estado_atual = None
bloqueado = False

def bloquear_teclado():
    global bloqueado
    if not bloqueado:
        print("Bloqueando teclado")
        keyboard.hook(lambda e: False)
        bloqueado = True

def desbloquear_teclado():
    global bloqueado
    if bloqueado:
        print("Desbloqueando teclado")
        keyboard.unhook_all()
        bloqueado = False

while True:
    try:
        res = requests.get("http://localhost:8000", timeout=1)
        estado = res.json()["teclado"]

        if estado != estado_atual:
            print("Novo estado:", estado)

            if estado == "bloqueado":
                bloquear_teclado()
            else:
                desbloquear_teclado()

            estado_atual = estado

    except Exception as e:
        print("Erro:", e)

    time.sleep(1)