# 🛜 Serve de Teste Icounter
> Este documento detalha os passos necessários para simular um servidor fake para ambinte de teste utilizado pelos equipamentos iCounter

## 📁 ESTRUTURA DO PROJETO:
```
SERVIDOR/
    ├── README.md           # Instruções completas, oque você está a ler agora
    ├── serve.py            # Código Python do serve
    ├── serve.sh            # Script shell para Linux
    ├── serve.bat           # Script batch para Windows
    └── requirements.txt    # Dependências Python
```

Serve TCP/HTTP para testes de comunicação com equipamentos Icounter (3D, 5D, VET, VS, 3S, 5S).



## 🐧 Linux:
**Torne o script executável**
```
chmod +x serve.sh
```
**Execute**
```
./serve.sh
```

## ⊞ Windows
Clique duas vezes em 
```
'serve.bat'
```
Ou execute no PowerShell:
```
.\serve.bat
```

# 📋 Pré-requisitos
**🐧 Linux (Ubuntu/Debian/Fedora):**
```
# Instale Python 3 (se não tiver)
sudo apt install python3 python3-pip  # Ubuntu/Debian
sudo dnf install python3 python3-pip  # Fedora
```

**⊞ Windows:**
```
Baixe Python 3.8+ de https://www.python.org/

Marque "Add Python to PATH" durante instalação

Verifique instalação: python3 --version
```

# 🎯 Como Usar
**Opção 1: Script Automático (Recomendado)**
```
./serve.sh
```
**⊞ Windows:**
```
serve.bat
```

**Opção 2: Python Direto**
```
python3 serve.py
```

# 📊 O que o Serve Faz
- Escuta conexões na porta configurada (padrão: 5000)
- Recebe dados dos equipamentos Icounter
- Salva em JSON no arquivo dados.json
- Mostra logs no terminal
- Responde ao equipamento com confirmação


# 🔧 Configuração do Equipamento
No equipamento Icounter, configure:
```
IP do Servidor: [IP_DESTE_COMPUTADOR]:5000
Tipo: TCP
```
Para descobrir o IP deste computador, veja a mensagem inicial do serve.

# 📝 Exemplo de Saída
```
============================================================
🚀 SERVIDOR ICOUNTER INICIADO
============================================================
📡 IP Local: 192.168.0.77
🔌 Porta: 5000
🌐 Endereço: tcp://192.168.0.77:5000
💾 Salvando dados em: dados.json
🖥️  Sistema: Linux
============================================================
⏳ Aguardando conexões...

[14:30:25] ✅ Nova conexão de: 192.168.0.164:55000
📦 Dados recebidos: 1200 bytes
✅ JSON válido detectado!
   └─ name: Paciente Teste
   └─ model: IcounterVet
📤 Resposta enviada: Dados recebidos
```

# ⚠️ Notas Importantes
- Mantenha o terminal aberto enquanto o serve roda
- Para parar: Ctrl+C
- Dados são salvos automaticamente
- Compatível com todos modelos Icounter
