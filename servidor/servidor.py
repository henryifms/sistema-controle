import serial
import socket
import threading
import psycopg2
import time
import subprocess
import os
from datetime import datetime

# ============ CONFIGURAÇÃO DO BANCO ============
DB_CONFIG = {
    'dbname': 'controle_labs',
    'user': 'admin',
    'password': '12345678',
    'host': 'localhost',
    'port': 5433
}

def get_conexao():
    return psycopg2.connect(**DB_CONFIG)

def obter_sala(ip):
    """Retorna o nome do laboratório associado ao IP, ou None."""
    try:
        conn = get_conexao()
        cur = conn.cursor()
        cur.execute("""
            SELECT l.nome FROM maquinas m 
            JOIN laboratorios l ON l.id = m.id_laboratorio
            WHERE m.ip = %s
        """, (ip,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Erro ao consultar sala para {ip}: {e}")
        return None

# ============ ARDUINO ============
try:
    arduino = serial.Serial('COM12', 9600, timeout=0.1)
    print("Arduino conectado!")
except:
    arduino = None
    print("Arduino não conectado (modo teste)")

# ============ SERVIDOR ============
IP_SERVIDOR = '0.0.0.0'
PORTA_REDE = 5000

clientes = {}
lock = threading.Lock()
admin_clients = []

TUNNEL_FILE = "tunnel_address.txt"

def criar_tunnel_ssh(porta_local):
    """
    Cria um túnel TCP público usando localhost.run (SSH reverso).
    Retorna o endereço público (host:porta).
    """
    try:
        print("\nCriando túnel público via localhost.run...")
        
        # Comando SSH reverso: expõe porta_local para o mundo
        cmd = [
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-R", f"80:localhost:{porta_local}",
            "nokey@localhost.run"
        ]
        
        # Inicia o processo SSH em background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Lê a saída para capturar o endereço público
        public_url = None
        timeout = 15  # segundos
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            # Procura por padrões de URL na saída
            line = line.strip()
            if line:
                print(f"   [SSH] {line}")
                
                # localhost.run geralmente mostra algo como:
                # "Connect to http://XXXXXXXXX.lhr.life or https://XXXXXXXXX.lhr.life"
                if "lhr.life" in line or "localhost.run" in line:
                    # Extrai o hostname
                    import re
                    match = re.search(r'([a-zA-Z0-9]+\.lhr\.life)', line)
                    if match:
                        hostname = match.group(1)
                        public_url = f"{hostname}:80"
                        break
        
        if public_url:
            # Salva no arquivo
            with open(TUNNEL_FILE, "w") as f:
                f.write(public_url)
            
            print(f"\n TÚNEL PÚBLICO CRIADO:")
            print(f"   {public_url}")
            print(f"   Endereço salvo em {TUNNEL_FILE}")
            print(f"    Os clientes devem conectar em: {public_url}\n")
            return process, public_url
        else:
            # Tenta extrair do stderr também
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"   [SSH err] {stderr_output}")
            
            print(" Não foi possível obter o endereço público")
            print("   O servidor funcionará apenas localmente.")
            return None, None
            
    except FileNotFoundError:
        print(" SSH não encontrado. Instale com: sudo apt install openssh-client")
        return None, None
    except Exception as e:
        print(f" Erro ao criar túnel SSH: {e}")
        return None, None

# ============ FUNÇÕES DO SERVIDOR ============
def enviar_para_sala(sala, comando):
    with lock:
        for client, info in list(clientes.items()):
            if info['sala'] == sala:
                try:
                    client.sendall((comando + "\n").encode())
                except:
                    remover_cliente(client)

def broadcast_admin(mensagem):
    with lock:
        for admin_client in admin_clients:
            try:
                admin_client.sendall((f"ADMIN:{mensagem}\n").encode())
            except:
                admin_clients.remove(admin_client)

def remover_cliente(client):
    with lock:
        if client in clientes:
            info = clientes[client]
            ip = info['ip']
            sala = info['sala']
            del clientes[client]
            
            mensagem = f"DESCONECTADO|{ip}|{sala}|{datetime.now().strftime('%H:%M:%S')}"
            print(f"[OBSERVADOR] {mensagem}")
            broadcast_admin(mensagem)

def verificar_heartbeats():
    while True:
        time.sleep(10)
        agora = time.time()
        with lock:
            clientes_offline = []
            for client, info in list(clientes.items()):
                if agora - info['ultimo_heartbeat'] > 30:
                    clientes_offline.append(client)
            for client in clientes_offline:
                info = clientes[client]
                print(f"[HEARTBEAT] Cliente {info['ip']} não responde, removendo...")
                remover_cliente(client)

def enviar_heartbeats():
    while True:
        time.sleep(15)
        with lock:
            for client, info in list(clientes.items()):
                try:
                    client.sendall(b"PING\n")
                except:
                    remover_cliente(client)

def escutar_cliente(client, addr):
    ip_cliente = addr[0]
    sala = obter_sala(ip_cliente)
    
    with lock:
        clientes[client] = {
            'ip': ip_cliente,
            'sala': sala,
            'ultimo_heartbeat': time.time()
        }
    
    print(f"Cliente conectado: {ip_cliente} | Sala: {sala}")
    mensagem = f"CONECTADO|{ip_cliente}|{sala}|{datetime.now().strftime('%H:%M:%S')}"
    broadcast_admin(mensagem)
    
    client.settimeout(2)
    
    while True:
        try:
            dados = client.recv(1024)
            if not dados:
                break
            mensagem = dados.decode().strip()
            
            with lock:
                if client in clientes:
                    clientes[client]['ultimo_heartbeat'] = time.time()
            
            if mensagem == "PONG":
                continue
            if mensagem == "REGISTER_ADMIN":
                with lock:
                    if client not in admin_clients:
                        admin_clients.append(client)
                        print(f"Administrador registrado: {ip_cliente}")
                continue
            
            if ":" in mensagem:
                sala_destino, comando = mensagem.split(":", 1)
                if sala_destino == "ALL":
                    print(f"[BROADCAST] {comando}")
                    with lock:
                        for c in list(clientes.keys()):
                            try:
                                c.sendall((comando + "\n").encode())
                            except:
                                remover_cliente(c)
                else:
                    print(f"[{sala_destino}] {comando}")
                    enviar_para_sala(sala_destino, comando)
                
                if arduino:
                    try:
                        arduino.write((f"{sala_destino}:{comando}\n").encode())
                    except Exception as e:
                        print(f"Erro ao enviar para Arduino: {e}")
            else:
                print(f"Comando inválido de {ip_cliente}: {mensagem}")
        
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Erro com {ip_cliente}: {e}")
            break
    
    remover_cliente(client)
    client.close()
    print(f"Cliente desconectado: {ip_cliente}")

def gerenciar_clientes():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP_SERVIDOR, PORTA_REDE))
    server.listen(10)
    print(f"Servidor local ouvindo em 0.0.0.0:{PORTA_REDE}")
    
    while True:
        client, addr = server.accept()
        threading.Thread(target=escutar_cliente, args=(client, addr), daemon=True).start()

# ============ INICIALIZAÇÃO ============
if __name__ == "__main__":
    # Verifica se SSH está disponível
    ssh_disponivel = False
    try:
        result = subprocess.run(["which", "ssh"], capture_output=True, text=True)
        ssh_disponivel = result.returncode == 0
    except:
        pass
    
    if not ssh_disponivel:
        print("⚠ SSH não encontrado. Instale com: sudo apt install openssh-client")
        print("   O servidor funcionará apenas localmente.\n")
    
    # Cria o túnel SSH se disponível
    tunnel_process = None
    if ssh_disponivel:
        tunnel_process, public_url = criar_tunnel_ssh(PORTA_REDE)
    
    # Inicia as threads
    threading.Thread(target=gerenciar_clientes, daemon=True).start()
    threading.Thread(target=verificar_heartbeats, daemon=True).start()
    threading.Thread(target=enviar_heartbeats, daemon=True).start()
    
    print("\nSistema iniciado! Pressione Ctrl+C para parar.")
    
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
                                remover_cliente(c)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDesligando servidor...")
        if tunnel_process:
            tunnel_process.terminate()
        if arduino:
            arduino.close()
