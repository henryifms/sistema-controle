import serial
import socket
import threading

# Configurações
arduino = serial.Serial('COM13', 9600, timeout=0.1)

# Configurações da Rede
IP_SERVIDOR = '0.0.0.0' # Escuta todas as placas de rede
PORTA_REDE = 5000
clientes = []

def gerenciar_clientes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP_SERVIDOR, PORTA_REDE))
    server.listen(5)
    print(f"Servidor de rede rodando na porta {PORTA_REDE}...")
    
    while True:
        client, addr = server.accept()
        print(f"PC conectado: {addr}")
        clientes.append(client)

# Rodar a espera por conexões em segudo plano
threading.Thread(target=gerenciar_clientes, daemon=True).start()

try:
    while True:
        if arduino.in_waiting > 0:
            comando = arduino.readline().decode('utf-8').strip()
            if comando:
                print(f"Enviando para rede: {comando}")
                # Envia o comando para todos os PCs conectados!!
                for c in clientes[:]:
                    try:
                        c.sendall((comando + "\n").encode())
                    except:
                        clientes.remove(c)
except KeyboardInterrupt:
    print("Desligando...")
