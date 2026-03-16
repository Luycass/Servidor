#!/usr/bin/env python3
import socket
import json
import time
import os
import subprocess
import platform

# ---------------------------------------------------------
# FUNÇÃO: run_command
# Executa comandos no terminal e ignora erros
# ---------------------------------------------------------
def run_sys_commands(port):
    print("🛠️  Executando preparações de sistema...")
    try:
        # 1. Tenta matar processos na porta 5000 (TCP e UDP)
        subprocess.run(["sudo", "fuser", "-k", f"{port}/tcp"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "fuser", "-k", f"{port}/udp"], stderr=subprocess.DEVNULL)
        
        # 2. Garante que a porta está aberta no Firewall do Fedora (Firewalld)
        subprocess.run(["sudo", "firewall-cmd", "--add-port", f"{port}/tcp"], stderr=subprocess.DEVNULL)
        
        # 3. Se o SELinux estiver bloqueando, isso ajuda (comum no Fedora)
        # subprocess.run(["sudo", "setenforce", "0"], stderr=subprocess.DEVNULL) # Opcional: Desativa SELinux temporariamente
        
        print("✅ Comandos de liberação enviados.")
    except Exception as e:
        print(f"⚠️ Aviso ao executar comandos: {e}")

# ---------------------------------------------------------
# FUNÇÃO: get_linux_ips
# ---------------------------------------------------------
def get_linux_ips():
    try:
        output = subprocess.check_output(['hostname', '-I']).decode().strip().split()
        # Filtra apenas IPv4 reais e ignora Docker (172.)
        ips = [ip for ip in output if "." in ip and not ip.startswith('172.')]
        return ips if ips else ["127.0.0.1"]
    except:
        return ["127.0.0.1"]

# ---------------------------------------------------------
# FUNÇÃO: save_to_json
# ---------------------------------------------------------
def save_to_json(data, filename="dados.json"):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    file_data = json.load(f)
                except:
                    file_data = []
        else:
            file_data = []
        
        if not isinstance(file_data, list): file_data = [file_data]
        
        entry = data.copy() if isinstance(data, dict) else {"raw_data": str(data)}
        entry["received_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
        file_data.append(entry)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

# ---------------------------------------------------------
# FUNÇÃO: start_server
# ---------------------------------------------------------
def start_server():
    PORT = 5000
    
    # Executa a limpeza antes de tudo
    run_sys_commands(PORT)
    
    ips = get_linux_ips()

    print("\n" + "="*60)
    print("🐧 SERVIDOR ICOUNTER - FEDORA EDITION (FORÇA BRUTA)")
    print("="*60)
    print("📡 ENDEREÇOS DISPONÍVEIS:")
    for ip in ips:
        print(f"   🚀 http://{ip}:{PORT}")
    print("-" * 60)
    print(f"💾 Salvando em: {os.path.abspath('dados.json')}")
    print("="*60)
    print("⏳ Aguardando conexão do equipamento...\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Ouve em todas as interfaces
        server_socket.bind(("0.0.0.0", PORT))
        server_socket.listen(5)

        while True:
            client_socket, client_address = server_socket.accept()
            client_ip = client_address[0]
            print(f"✅ Conexão detectada de: {client_ip}")

            try:
                client_socket.settimeout(3.0)
                data = client_socket.recv(16384)
                
                if data:
                    msg = data.decode("utf-8", errors="replace").strip()
                    print(f"📦 Dados recebidos (IP: {client_ip})")
                    
                    try:
                        json_data = json.loads(msg)
                        save_to_json(json_data)
                    except:
                        save_to_json({"raw": msg, "origin": client_ip})
                        
                    client_socket.sendall(b'{"status":"success"}\n')
            except Exception as e:
                print(f"❌ Erro no processamento: {e}")
            finally:
                client_socket.close()

    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()