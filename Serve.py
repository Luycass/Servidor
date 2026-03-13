#!/usr/bin/env python3
# Servidor TCP para teste do Icounter
# Recebe mensagens JSON do equipamento e salva em dados.json

import socket
import json
import time
import os
import platform

# -------------------------------
# Descobrir IP local
# -------------------------------
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# -------------------------------
# Encontrar porta disponível
# -------------------------------
def find_available_port(start_port=5000):
    port = start_port
    while port < 65535:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('0.0.0.0', port))
            s.close()
            return port
        except OSError:
            port += 1
    return None

# -------------------------------
# Salvar dados recebidos
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
    # Se vierem múltiplos JSONs grudados, tentamos tratar o split básico
    # No Ruby, lembre-se de enviar com \n no final
    messages = msg.strip().split("\n")
    
    last_response = {"status": "success", "message": "Recebido"}

    for m in messages:
        m = m.strip()
        if not m: continue
        
        print(f"  > {m}")
        try:
            json_data = json.loads(m)
            print("  ✅ JSON válido detectado!")
            save_to_json(json_data)
        except json.JSONDecodeError:
            print("  📋 Dados recebidos não são JSON puro")
            save_to_json({"raw_message": m, "client_ip": client_ip})

    return json.dumps(last_response).encode("utf-8")

# -------------------------------
# Servidor principal (Versão Robusta)
# -------------------------------
def start_server():
    local_ip = get_local_ip()
    port = find_available_port(5000)

    if port is None:
        print("❌ Nenhuma porta disponível")
        return

    # Cabeçalho original preservado
    print("\n" + "="*60)
    print("🛜 SERVIDOR ICOUNTER INICIADO")
    print("="*60)
    print(f"📡 IP: {local_ip}")
    print(f"🔌 Porta: {port}")
    print(f"🌐 Endereço: tcp://{local_ip}:{port}")
    print(f"💾 Salvando em: dados.json")
    print(f"🖥️ Sistema: {platform.system()}")
    print("="*60)
    print("⏳ Aguardando conexões...\n")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reiniciar o servidor sem erro de "Address already in use"
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(5)

        while True:
            # Aguarda nova conexão
            client_socket, client_address = server_socket.accept()
            client_ip = client_address[0]
            
            print("\n" + "─"*60)
            print(f"✅ Conexão de {client_ip}:{client_address[1]}")

            try:
                # Timeout de 3 segundos para não travar o servidor
                client_socket.settimeout(3.0)
                
                # Leitura direta do buffer (sem o loop while que causava travamento)
                data = client_socket.recv(8192)

                if data:
                    print(f"📦 {len(data)} bytes recebidos")
                    msg = data.decode("utf-8", errors="replace").strip()
                    
                    # Processa e gera resposta
                    response = process_message(msg, client_ip)
                    
                    # Envia resposta de volta (importante para fechar o ciclo TCP)
                    client_socket.sendall(response)
                else:
                    print("⚠️ Conexão aberta, mas vazia.")

            except socket.timeout:
                print(f"⏳ Tempo esgotado aguardando dados de {client_ip}")
            except Exception as e:
                print(f"❌ Erro durante a conexão: {e}")
            finally:
                # O ponto crucial: SEMPRE fecha o socket do cliente aqui
                client_socket.close()
                print("🔌 Conexão encerrada")

    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("🛑 Servidor encerrado")
        print("="*60)
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()