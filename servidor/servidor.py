import serial
import socket
import threading
import os  # Importar para verificar se o arquivo existe

# Nome do arquivo de configuração
CONFIG_FILE = "config.txt"

if os.path.exists(CONFIG_FILE):
    # Lê a porta salva
    with open(CONFIG_FILE, "r") as f:
        PORTA_REDE = int(f.read().strip())
        print(f"Porta {PORTA_REDE} carregada do arquivo {CONFIG_FILE}.")
else:
    while True:
        try:
            nova_porta = int(input("Primeira execução! Digite a porta para o servidor: "))
            # Salva a porta no arquivo
            with open(CONFIG_FILE, "w") as f:
                f.write(str(nova_porta))
            PORTA_REDE = nova_porta
            print(f"Porta {PORTA_REDE} salva com sucesso em {CONFIG_FILE}.")
            break
        except ValueError:
            print("Por favor, digite um número válido.")

arduino = serial.Serial('COM13', 9600, timeout=0.1) 

# Configurações da Rede
IP_SERVIDOR = '0.0.0.0' # Escuta todas as placas de rede
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

# Rodar a espera por conexões em segundo plano
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

