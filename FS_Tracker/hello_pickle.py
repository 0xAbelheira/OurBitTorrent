# PICKLE
import pickle

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

# Serializar a mensagem usando pickle
serialized_message = pickle.dumps(hello_message)

# Enviar a mensagem serializada

# ---------- Tracker ----------#

# Receber a mesagem serializada
# Converter a mensagem para dicionario
received_serialized_message = serialized_message
received_hello_message = pickle.loads(received_serialized_message)

# Acessar os campos da mensagem
received_node_ip = received_hello_message["ip"]
received_files = received_hello_message["files"]

# Acessar informação
for file, info in received_files.items():
    print(f"File: {file}")
    print(f"Blocks: {info['blocks']}")
    print()
