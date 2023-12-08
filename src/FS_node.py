import socket
import logging
import time
import threading
from file import File

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
            node_socket.connect(self.tracker_host, self.tracker_port)
            
            files_str = "\n".join(
                f"{file.name}:{file.size}:{file.num_blocks}:{','.join(map(str, file.blocks_available))}"
                for file in self.files
            )
            
            message = f"HELLO:{files_str}"
            
            msg = bytes(f"{len(message)}@", "utf-8") + message.encode("utf-8")
            
            node_socket.sendall(msg)
            
            response = node_socket.recv(1024).decode('utf-8')
            print(response);
        
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
    
        pass
    
    def handle_message(self, message, addr):
        # Implement logic to handle different types of messages
        # Example: Check message type and call corresponding methods
        pass

    def send_file(self, message):
        #Retirar de message o tipo da menssagem, o nome do ficheiro, e os blocos que se querem para download
        #procurar por esse file no node e enviar

        parts = message.split(";")
        if len(parts) != 5:
            print("Formato de mensagem inválido")
            return

        type, ip, name, blocos_info, size = parts

        # Verifica se o tipo é "download"
        if type.lower() != "download": #ou GET?
            print("Tipo de mensagem inválido para envio de arquivo")
            return

        # Converte blocos para uma lista de inteiros
        blocos = []
        blocos_parts = blocos_info.split(",")
        for blocos_part in blocos_parts:
            if "-" in blocos_part:
                start, end = map(int, blocos_part.split("-"))
                blocos.extend(range(start, end + 1))
            else:
                blocos.append(int(blocos_part))

        # Converte tamanho para inteiro
        try:
            size = int(size)
        except ValueError:
            print("Valor inválido para tamanho")
            return

        # Verifica se o arquivo existe
        if name not in self.files:
            print(f"O arquivo {name} não foi encontrado no nó")
            return

        # Verifica se todos os blocos solicitados estão disponíveis
        blocos_disponiveis = self.files[name]['blocks_available']
        if not all(block in blocos_disponiveis for block in blocos):
            print("Alguns blocos solicitados não estão disponíveis")
            return

        #print(f"Enviando arquivo {name} para {ip}")
    
    def ask_file(self, filename):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tracker_socket:
            tracker_socket.connect(self.tracker_host, self.tracker_port)
            
            message = f"GET:{filename}"
            msg = bytes(f"{len(message)}@", "utf-8") + message.encode("utf-8")
            tracker_socket.sendall(msg)
            
            response = tracker_socket.recv(1024).decode('utf-8')
            print(response);
            
            file_info = tracker_socket.recv(1024).decode('utf-8')
            
            info = self.choose_ip(file_info)
            tracker_socket.close()
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as node_socket:
            node_socket.connect(self.host, info)
        #TODO Criar conexão com outro peer e pedir o ficheiro
        #TODO Criar mensagem DOWNLOAD
    
    #TODO Retirar do info os ip que queremos aceder e quais os blocos a retirar de cada ip
    def choose_ip(self, info):
        pass
            
if __name__ == "__main__":
    # Creating five instances of the File class
    file1 = File("file1.txt", 1024)
    file2 = File("file2.jpg", 2048)
    file3 = File("file3.docx", 3072)
    file4 = File("file4.pdf", 4096)
    file5 = File("file5.txt", 512)
    # Displaying information about each
    files = [file1,file2,file3,file4,file5]
    node = Node('localhost', 50000, HOST, PORT, files)
    node.send_info_tracker()
    node.ask_file("file2.jpg")
    #conectar ao tracker e enviar a informação
    #inicializar o servidor
    #sempre que houver uma alteração na quantidade de ficheiros ou blocos, enviar um base de dados atualizada
    