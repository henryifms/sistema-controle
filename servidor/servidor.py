import serial
import socket
import threading

try:
    arduino = serial.Serial('COM12', 9600, timeout=0.1)
    print("Arduino conectado!")
except:
    arduino = None
    print("Arduino n conectado (teste)")

IP_SERVIDOR = '0.0.0.0'
PORTA_REDE = 5000
clientes = []

def escutar_cliente(client):
    while True:
        try:
            dados = client.recv(1024)
            if not dados:
                break

            comando = dados.decode().strip()
            print(f"Comando recebido: {comando}")

            for c in clientes[:]:
                try:
                    c.sendall((comando + "\n").encode())
                except:
                    clientes.remove(c)

        except:
            break

    if client in clientes:
        clientes.remove(client)
    client.close()

def gerenciar_clientes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP_SERVIDOR, PORTA_REDE))
    server.listen(5)
    print(f"Servidor de rede rodando na porta {PORTA_REDE}...")

    while True:
        client, addr = server.accept()
        print(f"PC conectado: {addr}")
        clientes.append(client)

        threading.Thread(target=escutar_cliente, args=(client,), daemon=True).start()

        try:
            if arduino:
                arduino.write(b"CLIENTE_CONECTADO\n")
        except:
            pass

threading.Thread(target=gerenciar_clientes, daemon=True).start()

try:
    while True:
        if arduino and arduino.in_waiting > 0:
            comando = arduino.readline().decode('utf-8').strip()
            if comando:
                print(f"Enviando para rede: {comando}")
                for c in clientes[:]:
                    try:
                        c.sendall((comando + "\n").encode())
                    except:
                        clientes.remove(c)
except KeyboardInterrupt:
    print("Desligando...")
