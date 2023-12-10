import socket
import logging
import json
import time
import threading
from file import File

logging.basicConfig(filename='node.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


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
        self.downloaded_blocks = set()

    def send_info_tracker(self):
        """
        Establishes a connection with the tracker and sends a 'hello' message containing file information.
        Prints the response received from the tracker.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.connect((self.tracker_host, self.tracker_port))
            
            files_str = "\n".join(
                f"{file.name}:{file.size}:{file.num_blocks}:{','.join(map(str, file.blocks_available))}"
                for file in self.files
            )
            message = f"HELLO:{files_str}"
            
            logging.debug(f"Message to send - {message}")
            
            msg = bytes(f"{len(message)}@", "utf-8") + message.encode("utf-8")
            
            node_socket.sendall(msg)
            
            response = node_socket.recv(1024).decode('utf-8')
            logging.info(f"{response}");
            
    def start_server_side(self):
        server_thread = threading.Thread(target=self.server_thread)
        server_thread.start()
        
    def server_thread(self):
        logging.info(f"Starting Server...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind((self.host, self.port))

            while True:
                data, addr = server_socket.recvfrom(1024)
                if data:
                    logging.info(f"Received data from {addr}")
                    client_handler_thread = threading.Thread(target=self.client_handler, args=(data, addr))
                    client_handler_thread.start()

    def client_handler(self, message, addr):
        with self.lock:
            logging.debug(f"Message from udp connection - {message}")
            if message.startswith(b"DOWNLOAD:"):
                logging.info(f"DOWNLOAD msg, received from {addr}")
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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tracker_socket:
                tracker_socket.connect((self.tracker_host, self.tracker_port))

                message = f"GET:{filename}"
                logging.debug(f"Message to send - {message}")
                msg = bytes(f"{len(message)}@", "utf-8") + message.encode("utf-8")

                tracker_socket.sendall(msg)

                response = self.handle_msg_size(tracker_socket).decode('utf-8')
                logging.info(f"{response}")

                file_info = self.handle_msg_size(tracker_socket).decode('utf-8')
                #BUG POR ALGUMA FUCKING RAZÃO, PRECISO DE DOIS DEBUG AQUI, SENÃO O PROGRAMA DÁ CRASH
                # SUSPEITO QUE TENHA A VER COM O TEMPO DE RECEBER MENSAGEM
                logging.debug(f"File info - {file_info}")
                
                download_info = self.choose_block_and_location(file_info)
                if download_info:
                    download_list, remaining_blocks = download_info

                    self.download_blocks(download_list, filename)

                    # Optionally, handle remaining blocks
                    logging.debug(f"Remaining blocks: {remaining_blocks}")

        except Exception as e:
            logging.error(f"Error in ask_file: {e}")
    
    
    def choose_block_and_location(self, file_info_list_str):
        try:
            peers_info = []
            
            file_info_lines = file_info_list_str.strip().split('\n')
            
            for line in file_info_lines:
                parts = line.split(':')
                
                if len(parts) == 3:
                    ip, blocks_available, total_blocks = parts
                    
                    # Convert blocks_available to a set of integers
                    blocks_available = set(map(int, blocks_available.split(',')))

                    # Calculate available blocks excluding already downloaded blocks
                    available_blocks = blocks_available - self.downloaded_blocks

                    if available_blocks:
                        peers_info.append({'ip': ip, 'blocks_available': available_blocks})

            if not peers_info:
                return None

            # Calculate all available blocks across peers
            all_available_blocks = set.union(*[peer['blocks_available'] for peer in peers_info])

            # Construct the download list and remaining blocks
            download_list = [{'ip': peer['ip'], 'blocks': sorted(list(peer['blocks_available']))} for peer in peers_info]
            remaining_blocks = sorted(list(all_available_blocks - set.union(*[peer['blocks_available'] for peer in peers_info])))

            logging.debug(f"Download list - {download_list}")
            logging.debug(f"Remaining_blocks list - {remaining_blocks}")
            
            return download_list, remaining_blocks
        except Exception as e:
            logging.error(f"Error in choose_block_and_location: {e}")
            return None

    def download_blocks(self, download_list, filename):
        try:
            for peer_info in download_list:
                ip = peer_info['ip']
                blocks_to_download = peer_info['blocks']

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as node_socket:
                    node_socket.connect((ip, self.port))

                    for block_to_download in blocks_to_download:
                        message = f"DOWNLOAD:{filename}:{block_to_download}"
                        logging.debug(f"Connected to - {ip}") 
                        logging.debug(f"Download message to send - {message}")
                        
                        msg = bytes(message, "utf-8")

                        node_socket.sendall(msg)

                        # Assuming the file_data is received through UDP
                        file_data, _ = node_socket.recvfrom(1024)

                        # Process the received file data (protocol-specific)
                        self.process_file_data(file_data)

                        # Update the set of downloaded blocks
                        self.downloaded_blocks.add(block_to_download)

        except Exception as e:
            logging.error(f"Error in download_blocks: {e}")

            
    def process_file_data(self, file_data):
        # Implement the logic to process received file data (protocol-specific)
        pass
    
    def handle_msg_size(self, conn):
        size_data = b''
        delimiter = b'@'

        while True:
            byte = conn.recv(1)
            if not byte or byte == delimiter:
                break

            size_data += byte

        try:
            msg_size = int(size_data.decode('utf-8'))
        except ValueError:
            logging.error("Invalid message size data")
            return None

        full_msg = b''

        while len(full_msg) < msg_size:
            remaining_size = msg_size - len(full_msg)
            chunk_size = min(1024, remaining_size)
            msg = conn.recv(chunk_size)

            if not msg:
                logging.error("Connection closed before receiving the full message")
                break

            full_msg += msg

        if len(full_msg) != msg_size:
            logging.error("Incomplete message received")

        return full_msg if len(full_msg) == msg_size else None
    
                
if __name__ == "__main__":
    file1 = File("file1.txt", 1024)
    file2 = File("file2.jpg", 2048)
    file3 = File("file3.docx", 3072)
    file4 = File("file4.pdf", 4096)
    file5 = File("file5.txt", 512)

    files = [file1, file2, file3, file4, file5]
    node = Node('localhost', 50000, HOST, PORT, files)
    node.send_info_tracker()

    # Start the server thread
    node.start_server_side()

    # Continue with other operations (e.g., asking for files)
    node.ask_file("file2.jpg")
    