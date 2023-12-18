import socket
import time
import logging
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
            
            response = node_socket.recv(1500).decode('utf-8')
            logging.info(f"{response}");
            
    def start_server_side(self):
        server_thread = threading.Thread(target=self.server_thread)
        server_thread.start()
        
    def server_thread(self):
        logging.info(f"Starting Server...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind((self.host, self.port))

            # Dictionary to keep track of whether ACK has been sent for a specific client
            ack_sent_dict = {}

            while True:
                data, addr = server_socket.recvfrom(1500)
                if data:
                    logging.info(f"Received data from {addr}")

                    # Send ACK only if it hasn't been sent for this client address
                    if addr not in ack_sent_dict or not ack_sent_dict[addr]:
                        ack_message = b"ACK"
                        server_socket.sendto(ack_message, addr)
                        ack_sent_dict[addr] = True

                    # Create a new thread to handle the client's request
                    client_handler_thread = threading.Thread(target=self.client_handler, args=(data, addr, server_socket, ack_sent_dict))
                    client_handler_thread.start()


    def client_handler(self, message, addr, server_socket, ack_sent_dict):
        with self.lock:
            logging.debug(f"Message from UDP connection - {message}")
            if message.startswith(b"DOWNLOAD:"):
                logging.info(f"DOWNLOAD msg, received from {addr}")
                data = self.select_data(message)
                server_socket.sendto(data, addr)
                logging.info(f"Enviado o bloco para o outro peer!")

                # Set ACK sent to False for the next message from this client
                ack_sent_dict[addr] = False


    def select_data(self, message):
        message = bytes(message)
        parts = message.decode("utf-8").split(":") 
        if len(parts) != 3:
            print("Formato de mensagem inválido")
            return

        msgtype, name, block_str = parts

        if msgtype.lower() != "download":
            print("Tipo de mensagem inválido para envio de arquivo")
            return

        file = File(name)

        for block in file.block_data:
            if block['block_number'] == int(block_str):
                data = block['data']

        logging.info(f"Selecionado bloco -{block_str}- com informacao: {data}")
        msg = bytes(f"{file.size}@", "utf-8") + data
        return msg
        
    
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
                
                logging.debug(f"File info - {file_info}")
                logging.debug(f"File info - {file_info}")
                
                download_info = self.choose_block_and_location(file_info)
                if download_info:
                    download_list, remaining_blocks = download_info

                    self.download_blocks(download_list, filename)

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
                    
                    blocks_available = set(map(int, blocks_available.split(',')))

                    available_blocks = blocks_available - self.downloaded_blocks

                    if available_blocks:
                        peers_info.append({'ip': ip, 'blocks_available': available_blocks})

            if not peers_info:
                return None

            all_available_blocks = set.union(*[peer['blocks_available'] for peer in peers_info])

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
            new_file = File()
            self.files.append(new_file)
            for peer_info in download_list:
                ip = peer_info['ip']
                blocks_to_download = peer_info['blocks']

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as node_socket:
                    node_socket.connect((ip, self.port))

                    for block_to_download in blocks_to_download:
                        ack_message = b"ACK"
                        node_socket.sendall(ack_message)

                        ack_received = self.wait_for_acknowledgment(node_socket)
                        
                        if not ack_received:
                            logging.error(f"No acknowledgment received from {ip} for block {block_to_download}. Aborting.")
                            self.files.pop()
                            return  

                        message = f"DOWNLOAD:{filename}:{block_to_download}"
                        logging.debug(f"Connected to - {ip}") 
                        logging.debug(f"Download message to send - {message}")
                        
                        msg = bytes(message, "utf-8")
                        node_socket.sendall(msg)

                        try:
                            file_data, _ = node_socket.recvfrom(1500)
                        except socket.timeout:
                            logging.error(f"Timeout waiting for data from {ip} for block {block_to_download}. Aborting.")
                            self.files.pop()
                            return  # Handle the error as needed

                        logging.info(f"Recebido bloco com informação {file_data}")
                        
                        parts = file_data.decode("utf-8").split('@')
                        if len(parts) != 2:
                            logging.error(f"Invalid data format{parts} received from {ip} for block {block_to_download}. Aborting.")
                            self.files.pop()
                            return  # Handle the error as needed

                        size, data = parts
                        size = int(size)
                        new_file.set_values(filename, size)
                        new_file.add_blockdata(data, block_to_download)
                        
                        self.send_info_tracker()
                            
            logging.info(f"Recebido ficheiro {filename} com informação")
            new_file.build_file()

        except Exception as e:
            logging.error(f"Error in download_blocks: {e}")


    def wait_for_acknowledgment(self, node_socket, timeout=3):
        start_time = time.time()
        ack_received = False

        while time.time() - start_time < timeout:
            try:
                ack, _ = node_socket.recvfrom(1500)
                if ack == b"ACK":
                    ack_received = True
                    break
            except socket.timeout:
                pass

        return ack_received

    
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
    file1 = File("/Users/hugoabelheira/Documents/GitHub/OurBitTorrent/File1.txt")
    file2 = File("/Users/hugoabelheira/Documents/GitHub/OurBitTorrent/File2.txt")
    file3 = File("/Users/hugoabelheira/Documents/GitHub/OurBitTorrent/File3.txt")
    file4 = File("/Users/hugoabelheira/Documents/GitHub/OurBitTorrent/File4.txt")
    files = [file1, file2, file3, file4]
    node = Node('localhost', 50000, HOST, PORT, files)
    node.send_info_tracker()

    # Start the server thread
    node.start_server_side()

    # Continue with other operations (e.g., asking for files)
    node.ask_file("/Users/hugoabelheira/Documents/GitHub/OurBitTorrent/File2.txt")
    