#!/usr/bin/env python3
# Servidor TCP Robusto para Icounter - Edição Fedora Multi-IP
import socket
import json
import time
import os
import platform
import subprocess

# -------------------------------
# Descobrir todos os IPs locais
# -------------------------------
def get_local_ips():
    try:
        # No Fedora, o hostname -I lista todos os IPs atribuídos às interfaces
        ips = subprocess.check_output(['hostname', '-I']).decode().strip().split()
        # Remove IPs internos de Docker ou máquinas virtuais (geralmente começam com 172)
        ips = [ip for ip in ips if not ip.startswith('172.')]
        return ips if ips else ["127.0.0.1"]
    except:
        return ["127.0.0.1"]

# -------------------------------
# Encontrar porta disponível
# -------------------------------
def find_available_port(start_port=5000):
    port = start_port
    while port < 65535:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Tenta dar bind apenas para testar se a porta está livre
            s.bind(('0.0.0.0', port))
            s.close()
            return port
        except OSError:
            port += 1
    return None

# -------------------------------
# Salvar dados recebidos em dados.json
# -------------------------------
def save_to_json(data, filename="dados.json"):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    file_data = json.load(f)
                except:
                    file_data = []
                if not isinstance(file_data, list):
                    file_data = [file_data]
        else:
            file_data = []

        entry = data.copy() if isinstance(data, dict) else {"raw_data": str(data)}
        entry["received_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
        file_data.append(entry)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar JSON: {e}")
        return False

# -------------------------------
# Processar mensagem recebida
# -------------------------------
def process_message(msg, client_ip):
    print(f"📝 Conteúdo recebido:")
    # Separa por quebra de linha caso o equipamento envie vários exames de uma vez
    messages = msg.strip().split("\n")
    
    last_response = {"status": "success", "message": "Recebido pelo Servidor"}

    for m in messages:
        m = m.strip()
        if not m: continue
        
        print(f"  └─ {m}")
        try:
            json_data = json.loads(m)
            print("     ✅ JSON válido!")
            save_to_json(json_data)
        except json.JSONDecodeError:
            print("     📋 Dados recebidos como texto plano")
            save_to_json({"raw_message": m, "client_ip": client_ip})

    return json.dumps(last_response).encode("utf-8")

# -------------------------------
# Servidor Principal
# -------------------------------
def start_server():
    all_ips = get_local_ips()
    port = find_available_port(5000)

    if port is None:
        print("❌ Nenhuma porta disponível")
        return

    print("\n" + "="*60)
    print("🛜  SERVIDOR ICOUNTER INICIADO - MODO ROBUSTO")
    print("="*60)
    print("📡 IPs DETECTADOS (Tente estes no equipamento):")
    for i, ip in enumerate(all_ips, 1):
        print(f"   {i}. {ip}:{port}")
    
    print("-" * 60)
    print(f"🔌 Porta Ativa: {port}")
    print(f"💾 Salvando em: {os.path.abspath('dados.json')}")
    print(f"🖥️  Sistema: {platform.system()} (Fedora)")
    print("="*60)
    print("⏳ Aguardando conexões...\n")

    # Criação do socket principal
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR evita o erro de "Address already in use" ao reiniciar rápido
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # 0.0.0.0 faz o servidor ouvir em TODAS as placas de rede ao mesmo tempo
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(5)

        while True:
            client_socket, client_address = server_socket.accept()
            client_ip = client_address[0]
            
            print(f"✅ Conexão estabelecida com {client_ip}")

            try:
                # Timeout de 3s para evitar que um socket "morto" trave o servidor
                client_socket.settimeout(3.0)
                
                # Lê o buffer (8KB é suficiente para os exames do Icounter)
                data = client_socket.recv(8192)

                if data:
                    print(f"📦 {len(data)} bytes recebidos")
                    msg = data.decode("utf-8", errors="replace").strip()
                    
                    # Processa mensagens e gera resposta confirmando recebimento
                    response = process_message(msg, client_ip)
                    client_socket.sendall(response)
                else:
                    print("⚠️ O equipamento conectou mas não enviou dados.")

            except socket.timeout:
                print(f"⏳ Timeout: O equipamento demorou demais para transmitir.")
            except Exception as e:
                print(f"❌ Erro na sessão: {e}")
            finally:
                # Fecha o socket do cliente para liberar o teste no Ruby
                client_socket.close()
                print("🔌 Conexão encerrada e porta liberada.")

    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("🛑 Servidor encerrado pelo usuário")
        print("="*60)
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()