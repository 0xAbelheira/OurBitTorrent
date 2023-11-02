# JSON
import json

# ---------- NODE ---------- #
# Exemplo de dados
node_ip = "192.168.1.1"
files = {
    "file1": {
        "blocks": [1, 2, 3]
    },
    "file2": {
        "blocks": [4, 5]
    }
}

# Criar a mensagem hello como um dicionário
hello_message = {
    "ip": node_ip,
    "files": files
}

# Converter para JSON
json_hello_message = json.dumps(hello_message)

# Enviar a mensagem JSON

# ---------- Tracker ----------#

# Receber a mesagem JSON

# Converter para dicionario
received_hello_message = json.loads(json_hello_message)

# Acessar os campos da mensagem
received_node_ip = received_hello_message["ip"]
received_files = received_hello_message["files"]

# Acessar informação
for file, info in received_files.items():
    print(f"File: {file}")
    print(f"Blocks: {info['blocks']}")
    print()
