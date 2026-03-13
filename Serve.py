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
                file_data = json.load(f)

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
    print(msg)

    try:
        json_data = json.loads(msg)

        print("✅ JSON válido detectado!")

        for key, value in json_data.items():
            print(f"   └─ {key}: {value}")

        save_to_json(json_data)

        response = {
            "status": "success",
            "message": "JSON recebido"
        }

    except json.JSONDecodeError:

        print("📋 Dados recebidos não são JSON")

        save_to_json({
            "raw_message": msg,
            "client_ip": client_ip
        })

        response = {
            "status": "success",
            "message": "Texto recebido"
        }

    return json.dumps(response).encode("utf-8")


# -------------------------------
# Servidor principal
# -------------------------------
def start_server():

    local_ip = get_local_ip()
    port = find_available_port(5000)

    if port is None:
        print("❌ Nenhuma porta disponível")
        return

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

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("0.0.0.0", port))

    server_socket.listen(5)

    try:

        while True:

            client_socket, client_address = server_socket.accept()

            client_ip = client_address[0]
            client_port = client_address[1]

            print("\n" + "─"*60)
            print(f"✅ Conexão de {client_ip}:{client_port}")

            client_socket.settimeout(3)

            data = b""

            try:

                # leitura completa do socket
                while True:

                    part = client_socket.recv(4096)

                    if not part:
                        break

                    data += part

            except socket.timeout:
                pass

            if data:

                try:
                    msg = data.decode("utf-8").strip()
                except:
                    msg = data.decode("utf-8", errors="replace").strip()

                print(f"📦 {len(data)} bytes recebidos")

                # separa mensagens caso venha mais de uma
                messages = msg.split("\n")

                for m in messages:

                    if m.strip():
                        response = process_message(m.strip(), client_ip)
                        client_socket.send(response)

            else:
                print("⚠️ Nenhum dado recebido")

            client_socket.close()

            print("🔌 Conexão encerrada")

    except KeyboardInterrupt:

        print("\n")
        print("="*60)
        print("🛑 Servidor encerrado")
        print("="*60)

    finally:

        server_socket.close()


# -------------------------------
# Execução
# -------------------------------
if __name__ == "__main__":
    start_server()
