import socket
import logging
import threading

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
HEADERSIZE = 15

class Node:
    def __init__(self, host, port, tracker_host, tracker_port, files):
        self.host = host
        self.port = port
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.lock = threading.RLock()
        self.files = files

    def send_info_tracker(self):
        """
        Establishes a connection with the tracker and sends a 'hello' message containing file information.
        Prints the response received from the tracker.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.connect((self.tracker_host, self.tracker_port))  # Fix here
            
            files_str = "\n".join(
                f"{key}:{value['ip']}:{','.join(map(str, value['blocks_available']))}:{value['total_blocks']}"
                for key, value in self.files.items()
            )
            
            message = f"HELLO:{files_str}"
            
            msg = bytes(f"{len(message)}@", "utf-8") + message.encode("utf-8")
            
            node_socket.sendall(msg)
    
    #//TODO verificar que o socket tem conexão com o exterior
    def start_server_side(self):
        #abrir um socket UDP e ficar a espera de uma conexão
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
        #quando receber a conexão, é necessário receber a mensagem e enviar a mensagem para um handler, para saber o que fazer
            while True:
                    msg, addr = server_socket.recvfrom(1024)  # Tamanho máximo dos dados recebidos (ajuste conforme necessário)

                    client_handler_thread = threading.Thread(target = self.handle_message, args=(msg, addr))
                    client_handler_thread.start()
    
    def send_file(self, message):
        #Retirar de message o tipo da menssagem, o nome do ficheiro, e os blocos que se querem para download
        #procurar por esse file no node e enviar

        parts = message.split(";")
        if len(parts) != 5:
            print("Formato de mensagem inválido")
            return

        tipo, ip_destino, nome_arquivo, blocos_str, tamanho = parts

        # Verifica se o tipo é "download"
        if tipo.lower() != "download": #ou GET
            print("Tipo de mensagem inválido para envio de arquivo")
            return

        # Converte blocos para uma lista de inteiros
        blocos = []
        blocos_parts = blocos_str.split(",")
        for blocos_part in blocos_parts:
            if "-" in blocos_part:
                start, end = map(int, blocos_part.split("-"))
                blocos.extend(range(start, end + 1))
            else:
                blocos.append(int(blocos_part))

        # Converte tamanho para inteiro
        try:
            tamanho = int(tamanho)
        except ValueError:
            print("Valor inválido para tamanho")
            return

        # Verifica se o arquivo existe
        if nome_arquivo not in self.files:
            print(f"O arquivo {nome_arquivo} não foi encontrado no nó")
            return

        # Verifica se todos os blocos solicitados estão disponíveis
        blocos_disponiveis = self.files[nome_arquivo]['blocks_available']
        if not all(block in blocos_disponiveis for block in blocos):
            print("Alguns blocos solicitados não estão disponíveis")
            return

        print(f"Enviando arquivo {nome_arquivo} para {ip_destino}")
    
    def ask_file(self):
        #pedir conexão ao tracker, perguntar sobre o ip onde está o ficheiro que queremos e blocos disponiveis
        #tracker devolve uma mensagem com a informação
        #utilizar essa informação para pedir o ficheiro ao ip correspondente
        return
        
            
            
if __name__ == "__main__":
    file1 =
    file2 =
    file3 =
    file4 =
    #conectar ao tracker e enviar a informação
    #inicializar o servidor
    #sempre que houver uma alteração na quantidade de ficheiros ou blocos, enviar um base de dados atualizada
    