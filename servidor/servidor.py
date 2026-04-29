import serial
import socket
import threading

# ARDUINO
try:
    arduino = serial.Serial('COM12', 9600, timeout=0.1)
    print("Arduino conectado!")
except:
    arduino = None
    print("Arduino n conectado (teste)")

# SERVIDOR
IP_SERVIDOR = '0.0.0.0'
PORTA_REDE = 5000

# client -> ip
clientes = {}

# salas
salas = {
    "lab1": ["10.8.33.159", "10.8.33.158"],
    "lab2": ["10.8.33.157", "10.8.33.156", "10.8.33.152"]
}

lock = threading.Lock()

# FUNÇÕEs 
def obter_sala(ip):
    for sala, ips in salas.items():
        if ip in ips:
            return sala
    return None

def enviar_para_sala(sala, comando):
    with lock:
        for c, ip in list(clientes.items()):
            if obter_sala(ip) == sala:
                try:
                    c.sendall((comando + "\n").encode())
                except:
                    print(f"Erro ao enviar para {ip}, removendo...")
                    del clientes[c]

# THREAD CLIeNTE
def escutar_cliente(client, addr):
    ip_cliente = addr[0]

    with lock:
        clientes[client] = ip_cliente

    sala = obter_sala(ip_cliente)
    print(f"Cliente conectado: {ip_cliente} | Sala: {sala}")

    while True:
        try:
            dados = client.recv(1024)
            if not dados:
                break

            mensagem = dados.decode().strip()

            if ":" in mensagem:
                sala_destino, comando = mensagem.split(":", 1)

                print(f"[{sala_destino}] {comando}")

                enviar_para_sala(sala_destino, comando)

                # enviar pro Arduino
                if arduino:
                    try:
                        arduino.write((mensagem + "\n").encode())
                    except:
                        pass
            else:
                print(f"Comando inválido de {ip_cliente}: {mensagem}")

        except Exception as e:
            print(f"Erro com {ip_cliente}: {e}")
            break

    # desconexão
    with lock:
        if client in clientes:
            del clientes[client]

    client.close()
    print(f"Cliente desconectado: {ip_cliente}")

# THREAD PRINCIPAL
def gerenciar_clientes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP_SERVIDOR, PORTA_REDE))
    server.listen(5)

    print(f"Servidor rodando na porta {PORTA_REDE}...")

    while True:
        client, addr = server.accept()
        threading.Thread(
            target=escutar_cliente,
            args=(client, addr),
            daemon=True
        ).start()

# INICIAR
threading.Thread(target=gerenciar_clientes, daemon=True).start()

try:
    while True:
        if arduino and arduino.in_waiting > 0:
            comando = arduino.readline().decode('utf-8').strip()

            if comando:
                print(f"Arduino - {comando}")

                with lock:
                    for c in list(clientes.keys()):
                        try:
                            c.sendall((comando + "\n").encode())
                        except:
                            del clientes[c]

except KeyboardInterrupt:
    print("Desligando...")
