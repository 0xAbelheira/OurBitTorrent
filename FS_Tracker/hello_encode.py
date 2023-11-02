# Codificação da mensagem "Hello" para bytes
node_ip = "192.168.1.1"
files = {
    "file1": [1, 2, 3],
    "file2": [4, 5]
}

# Codificação dos dados
encoded_node_ip = node_ip.encode("utf-8")
encoded_files = "|".join(
    [f"{file}:{','.join(map(str, blocks))}" for file, blocks in files.items()]).encode("utf-8")

# Adicionar um separador entre o IP e os dados do arquivo
separator = b"||"
message = encoded_node_ip + separator + encoded_files

# Enviar a mensagem

# Receber a mensagem
# received_message = ...

# Descodificação dos dados recebidos
decoded_data = received_message.split(separator)
received_node_ip = decoded_data[0].decode("utf-8")
received_files = {}
for file_info in decoded_data[1].decode("utf-8").split("|"):
    file, blocks = file_info.split(":")
    received_files[file] = list(map(int, blocks.split(",")))

# Acessar os valores descodificados
print(f"Node IP: {received_node_ip}")
for file, blocks in received_files.items():
    print(f"File: {file}")
    print(f"Blocks: {blocks}")
