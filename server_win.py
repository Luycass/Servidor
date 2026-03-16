import socket
import json
import os

HOST = "0.0.0.0"
PORT = 5000

arquivo_json = "dados.json"

print("============================================================")
print("🛜 SERVIDOR ICOUNTER INICIADO")
print("============================================================")

hostname = socket.gethostname()
ip_local = socket.gethostbyname(hostname)

print(f"📡 IP: {ip_local}")
print(f"🔌 Porta: {PORT}")
print(f"🌐 Endereço: tcp://{ip_local}:{PORT}")
print(f"💾 Salvando em: {arquivo_json}")
print("============================================================")
print("⏳ Aguardando conexões...\n")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)


while True:

    conn, addr = server.accept()

    print("────────────────────────────────────────────────────────────")
    print("✅ Nova conexão recebida")
    print(f"📡 IP do equipamento: {addr[0]}")
    print(f"🔌 Porta: {addr[1]}")
    print("────────────────────────────────────────────────────────────")

    try:

        buffer = ""

        while True:

            data = conn.recv(4096)

            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:

                linha, buffer = buffer.split("\n", 1)

                if linha.strip() == "":
                    continue

                try:

                    obj = json.loads(linha)

                    print("📦 JSON recebido:")
                    print(obj)

                    if os.path.exists(arquivo_json):

                        with open(arquivo_json, "r") as f:
                            dados = json.load(f)

                    else:
                        dados = []

                    dados.append(obj)

                    with open(arquivo_json, "w") as f:
                        json.dump(dados, f, indent=4)

                    print("💾 Dados salvos no JSON")

                except json.JSONDecodeError:

                    print("⚠️ Erro ao decodificar JSON:")
                    print(linha)

    except Exception as e:

        print("❌ Erro na conexão:", e)

    finally:

        conn.close()

        print("🔌 Conexão encerrada\n")