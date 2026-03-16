#!/usr/bin/env python3
import socket
import json
import time
import os
import subprocess

# ---------------------------------------------------------
# FUNÇÃO: get_linux_ip
# Pega o IP real do Fedora via hostname -I
# ---------------------------------------------------------
def get_linux_ips():
    try:
        # Pega todos os IPs e filtra o Docker e IPv6
        output = subprocess.check_output(['hostname', '-I']).decode().strip().split()
        ips = [ip for ip in output if "." in ip and not ip.startswith('172.')]
        return ips
    except Exception as e:
        print(f"Erro ao buscar IPs: {e}")
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
        print(f"❌ Erro ao salvar JSON: {e}")
        return False

# ---------------------------------------------------------
# FUNÇÃO: start_server
# ---------------------------------------------------------
def start_server():
    port = 5000
    ips = get_linux_ips()

    # Tenta liberar a porta no sistema antes de começar
    try:
        subprocess.run(["sudo", "fuser", "-k", f"{port}/tcp"], stderr=subprocess.DEVNULL)
    except:
        pass

    print("\n" + "="*50)
    print("🐧 SERVIDOR ICOUNTER - EDIÇÃO LINUX (FEDORA)")
    print("="*50)
    print("📡 Tente estes IPs no equipamento:")
    for ip in ips:
        print(f"   👉 {ip}:{port}")
    print("-" * 50)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # 0.0.0.0 para ouvir em todas as placas de rede
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(5)
        print(f"⏳ Aguardando conexões na porta {port}...")

        while True:
            client_socket, client_address = server_socket.accept()
            client_ip = client_address[0]
            print(f"\n✅ Conexão de: {client_ip}")

            try:
                client_socket.settimeout(3.0)
                data = client_socket.recv(8192)
                if data:
                    msg = data.decode("utf-8", errors="replace").strip()
                    print(f"📦 Dados: {msg[:50]}...") # Mostra o começo da mensagem
                    
                    # Processa JSON
                    try:
                        json_data = json.loads(msg)
                        save_to_json(json_data)
                    except:
                        save_to_json({"raw": msg, "ip": client_ip})
                    
                    # Resposta para o equipamento
                    client_socket.sendall(b'{"status":"success"}\n')
            except Exception as e:
                print(f"❌ Erro: {e}")
            finally:
                client_socket.close()

    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()