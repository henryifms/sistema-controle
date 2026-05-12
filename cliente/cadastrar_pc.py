import socket
import psycopg2
import argparse
import sys

def get_ip_local():
    """Obtém o IP real da máquina na rede"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Conecta a um IP externo para descobrir o IP local
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        # Fallback: tenta conexão com DNS do Google
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def testar_conexao(host, port):
    """Testa se o banco de dados está acessível"""
    try:
        conn = psycopg2.connect(
            dbname='controle_labs',
            user='admin',
            password='12345678',
            host=host,
            port=port,
            connect_timeout=3
        )
        conn.close()
        return True
    except Exception as e:
        print(f"Erro na conexão com banco: {e}")
        return False

def cadastrar(ip, laboratorio, host, port):
    """Cadastra ou atualiza máquina no banco"""
    try:
        conn = psycopg2.connect(
            dbname='controle_labs',
            user='admin',
            password='12345678',
            host=host,
            port=port
        )
        cur = conn.cursor()
        
        # Upsert: insere se não existir, atualiza se já existir
        cur.execute("""
            INSERT INTO maquinas (ip, id_laboratorio, ultima_atualizacao)
            VALUES (
                %s, 
                (SELECT id FROM laboratorios WHERE nome = %s),
                NOW()
            )
            ON CONFLICT (ip) DO UPDATE SET
                id_laboratorio = EXCLUDED.id_laboratorio,
                ultima_atualizacao = NOW()
        """, (ip, laboratorio))
        
        conn.commit()
        
        # Verifica se o laboratório existe
        if cur.rowcount == 0:
            print(f"⚠ Atenção: Laboratório '{laboratorio}' pode não existir!")
        else:
            print(f"✓ PC {ip} cadastrado/atualizado no laboratório '{laboratorio}'")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao cadastrar: {e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cadastra PC no sistema de controle de laboratórios')
    parser.add_argument('--lab', required=True, help='Nome do laboratório (ex: lab1, lab_info)')
    parser.add_argument('--host', default='localhost', help='IP do servidor PostgreSQL')
    parser.add_argument('--port', type=int, default=5433, help='Porta do PostgreSQL')
    parser.add_argument('--listar', action='store_true', help='Lista laboratórios disponíveis')
    
    args = parser.parse_args()
    
    print("=== Cadastro de Máquina - Sistema de Controle de Laboratórios ===\n")
    
    # Obtém IP local
    ip = get_ip_local()
    print(f"IP detectado: {ip}")
    
    # Testa conexão
    print(f"Testando conexão com {args.host}:{args.port}...")
    if not testar_conexao(args.host, args.port):
        print("\nNão foi possível conectar ao banco de dados.")
        print("Verifique:")
        print("  1. Se o servidor PostgreSQL está rodando")
        print("  2. Se o IP e porta estão corretos")
        print("  3. Se a VPN está ativa (se aplicável)")
        sys.exit(1)
    
    print("Conexão OK!\n")
    
    # Cadastra
    if cadastrar(ip, args.lab, args.host, args.port):
        print("\nCadastro realizado com sucesso!")
        print(f"Agora execute o cliente principal para receber comandos.")
    else:
        print("\nFalha no cadastro. Verifique os dados e tente novamente.")
        sys.exit(1)
