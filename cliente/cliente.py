import socket
import ctypes
from ctypes import wintypes
import os
import time
import argparse
import sys

# ============ CONFIGURAÇÕES DO WINDOWS ============
if os.name == 'nt':
    keybd_event = ctypes.windll.user32.keybd_event
    VK_RETURN = 0x0D
    KEYEVENTF_KEYUP = 0x0002
    
    BlockInput = ctypes.windll.user32.BlockInput
    BlockInput.argtypes = [wintypes.BOOL]
    BlockInput.restype = wintypes.BOOL
else:
    print("AVISO: Funções de bloqueio só funcionam no Windows")
    keybd_event = None
    BlockInput = None

def obter_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def travar_teclado():
    if BlockInput and BlockInput(True):
        print("Teclado e mouse BLOQUEADOS")
        return True
    else:
        print("Erro ao bloquear (execute como Administrador)")
        return False

def destravar_teclado():
    if BlockInput and BlockInput(False):
        print("Teclado e mouse DESBLOQUEADOS")
        return True
    else:
        print("Erro ao desbloquear")
        return False

def pressionar_enter_2x():
    if keybd_event:
        for _ in range(2):
            keybd_event(VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)

def processar_comando(mensagem, client):
    if mensagem == "PING":
        return "PONG"
    
    print(f"COMANDO RECEBIDO: {mensagem}")
    try:
        if mensagem == "BLOQUEAR_TECLADO":
            travar_teclado()
        elif mensagem == "DESBLOQUEAR_TECLADO":
            destravar_teclado()
        elif mensagem == "BLOQUEAR_TELA":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            time.sleep(1)
            travar_teclado()
        elif mensagem == "DESBLOQUEAR_TELA":
            destravar_teclado()
            time.sleep(1)
            pressionar_enter_2x()
        elif mensagem.startswith("STATUS:"):
            return f"ALIVE:{obter_ip_local()}"
        else:
            print(f"Comando desconhecido: {mensagem}")
    except Exception as e:
        print(f"Erro ao processar comando: {e}")
    return None

def conectar_servidor(host, porta):
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(5)
            client.connect((host, porta))
            print(f"✓ Conectado ao servidor {host}:{porta}")
            return client
        except Exception as e:
            print(f"✗ Erro ao conectar: {e}. Tentando novamente em 5s...")
            time.sleep(5)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', help='Endereço do servidor (host:porta ou só host)')
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor (padrão 5000)')
    parser.add_argument('--tunnel-file', default='tunnel_address.txt', help='Arquivo com endereço do túnel')
    args = parser.parse_args()
    
    # Determina host e porta
    host = None
    porta = args.port
    
    if args.server:
        # Pode ser "host:port" ou só "host"
        if ':' in args.server:
            host, port_str = args.server.split(':')
            porta = int(port_str)
        else:
            host = args.server
    else:
        # Tenta ler do arquivo de túnel gerado pelo servidor
        try:
            with open(args.tunnel_file, 'r') as f:
                tunnel_url = f.read().strip()
                # Formato: tcp://0.tcp.ngrok.io:12345
                if tunnel_url.startswith('tcp://'):
                    tunnel_url = tunnel_url[6:]  # remove 'tcp://'
                    host, port_str = tunnel_url.split(':')
                    porta = int(port_str)
                elif ':' in tunnel_url:
                    host, port_str = tunnel_url.split(':')
                    porta = int(port_str)
                else:
                    host = tunnel_url
        except Exception as e:
            print(f"Não foi possível ler {args.tunnel_file}: {e}")
    
    if not host:
        # Fallback para localhost
        host = 'localhost'
        print("Usando servidor local (localhost).")
    
    print(f"Conectando a {host}:{porta}...")
    client = conectar_servidor(host, porta)
    client.settimeout(2)
    
    while True:
        try:
            dados = client.recv(1024)
            if not dados:
                print("Conexão perdida!")
                break
            
            mensagem = dados.decode().strip()
            
            if mensagem == "PING":
                try:
                    client.sendall(b"PONG\n")
                except:
                    break
                continue
            
            resposta = processar_comando(mensagem, client)
            if resposta:
                try:
                    client.sendall((resposta + "\n").encode())
                except:
                    break
                    
        except socket.timeout:
            continue
        except (ConnectionResetError, ConnectionAbortedError):
            print("Conexão resetada.")
            break
        except Exception as e:
            print(f"Erro: {e}")
            break
    
    client.close()
    print("Tentando reconectar em 3 segundos...")
    time.sleep(3)
    main()

if __name__ == "__main__":
    main()
