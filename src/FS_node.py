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
        #quando receber a conexão, é necessário receber a mensagem e enviar a mensagem para um handler, para saber o que fazer
    
    def send_file(self, message):
        #Retirar de message o nome do ficheiro, e os blocos que se querem para download
        #procurar por esse file no node e enviar
    
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
    