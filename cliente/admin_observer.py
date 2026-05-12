import socket
import time
import threading
from datetime import datetime
import argparse
import sys

def conectar_admin(host, porta):
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, porta))
            client.sendall(b"REGISTER_ADMIN\n")
            print(f"✓ Conectado como ADMINISTRADOR a {host}:{porta}")
            return client
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}. Tentando novamente...")
            time.sleep(5)

class AdminObserver:
    def __init__(self, host, porta):
        self.client = None
        self.running = True
        self.laboratorios_status = {}
        self.host = host
        self.porta = porta

    def conectar(self):
        self.client = conectar_admin(self.host, self.porta)

    def processar_mensagem(self, mensagem):
        if mensagem.startswith("ADMIN:"):
            conteudo = mensagem[6:]
            if "|" in conteudo:
                partes = conteudo.split("|")
                if len(partes) >= 3:
                    evento = partes[0]
                    ip = partes[1]
                    sala = partes[2]
                    hora = partes[3] if len(partes) > 3 else datetime.now().strftime('%H:%M:%S')
                    
                    if evento == "CONECTADO":
                        print(f"[{hora}] CONECTADO  | IP: {ip:15} | Sala: {sala}")
                        self.laboratorios_status[ip] = "ONLINE"
                    elif evento == "DESCONECTADO":
                        print(f"[{hora}] DESCONECTADO | IP: {ip:15} | Sala: {sala}")
                        self.laboratorios_status[ip] = "OFFLINE"
        self.mostrar_status()

    def mostrar_status(self):
        online = sum(1 for s in self.laboratorios_status.values() if s == "ONLINE")
        offline = sum(1 for s in self.laboratorios_status.values() if s == "OFFLINE")
        total = len(self.laboratorios_status)
        if total > 0:
            print(f"\n📊 RESUMO: {online} online | {offline} offline | {total} total")
            print("-" * 50)

    def enviar_comando(self, sala, comando):
        if self.client:
            try:
                msg = f"{sala}:{comando}"
                self.client.sendall((msg + "\n").encode())
                print(f"✓ Comando enviado: [{sala}] {comando}")
            except Exception as e:
                print(f"✗ Erro ao enviar: {e}")

    def console_interativo(self):
        print("\n=== Console do Administrador ===")
        print("Comandos: status, enviar <sala> <cmd>, broadcast <cmd>, help, quit")
        while self.running:
            try:
                cmd = input("\n> ").strip()
                if cmd.lower() == 'quit':
                    self.running = False
                elif cmd.lower() == 'status':
                    self.mostrar_status()
                elif cmd.lower() == 'help':
                    print("status, enviar <sala> <cmd>, broadcast <cmd>, quit")
                elif cmd.startswith('enviar '):
                    partes = cmd.split(' ', 2)
                    if len(partes) >= 3:
                        self.enviar_comando(partes[1], partes[2])
                    else:
                        print("Uso: enviar <sala> <comando>")
                elif cmd.startswith('broadcast '):
                    self.enviar_comando("ALL", cmd[10:])
                else:
                    print("Comando desconhecido.")
            except KeyboardInterrupt:
                print("\nUse 'quit' para sair.")

    def run(self):
        self.conectar()
        console_thread = threading.Thread(target=self.console_interativo, daemon=True)
        console_thread.start()
        
        self.client.settimeout(2)
        while self.running:
            try:
                dados = self.client.recv(1024)
                if not dados:
                    print("Conexão perdida, reconectando...")
                    self.conectar()
                    continue
                mensagem = dados.decode().strip()
                if mensagem == "PING":
                    self.client.sendall(b"PONG\n")
                else:
                    self.processar_mensagem(mensagem)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erro: {e}")
                time.sleep(2)
        self.client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='Endereço do servidor (host:porta)')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--tunnel-file', default='tunnel_address.txt')
    args = parser.parse_args()
    
    host = None
    porta = args.port
    
    if args.server:
        if ':' in args.server:
            host, port_str = args.server.split(':')
            porta = int(port_str)
        else:
            host = args.server
    else:
        try:
            with open(args.tunnel_file, 'r') as f:
                tunnel_url = f.read().strip()
                if tunnel_url.startswith('tcp://'):
                    tunnel_url = tunnel_url[6:]
                    host, port_str = tunnel_url.split(':')
                    porta = int(port_str)
                elif ':' in tunnel_url:
                    host, port_str = tunnel_url.split(':')
                    porta = int(port_str)
                else:
                    host = tunnel_url
        except:
            host = 'localhost'
    
    observer = AdminObserver(host, porta)
    try:
        observer.run()
    except KeyboardInterrupt:
        print("\nEncerrando...")
        observer.running = False
        sys.exit(0)
