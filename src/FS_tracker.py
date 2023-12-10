import socket
import threading
import logging
from Database import Database

# Configure logging
logging.basicConfig(filename='tracker.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
HEADERSIZE = 15


class FSTrackProtocol:
    """
    Class for implementing the FS Track protocol for communication between nodes and the tracker.
    """

    def __init__(self, host, port):
        self.tracker = Tracker(host, port)

    def start_server(self):
        self.tracker.start_server()

    def view_database(self):
        self.tracker.view_database()

    def close_server(self):
        self.tracker.close()


class Tracker:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.database = Database()
        self.lock = threading.RLock()

    def start_server(self):
        logging.info(f"Starting Server...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            while True:
                conn, addr = server_socket.accept()
                logging.info(f"Connected by {addr}")
                client_handler_thread = threading.Thread(target=self.client_handler, args=(conn, addr))
                client_handler_thread.start()

    def client_handler(self, conn, addr):
        with self.lock:
            data = self.handle_msg_size(conn)
            if data.startswith(b"HELLO:"):
                self.handle_hello_message(data, addr[0])
                conn.sendall(
                    bytes(f"HELLO msg, received and processed for {addr}", "utf-8"))
            elif data.startswith(b"GET:"):
                file_info = self.handle_get_message(data, addr[0])
                if file_info:
                    response = "GET msg, received and processed for {addr}"
                    conn.sendall(bytes(f"{len(response)}@", "utf-8") + response.encode("utf-8"))

                    conn.sendall(bytes(f"{len(file_info)}@", "utf-8") + file_info.encode("utf-8"))
                else:
                    logging.warning(f"File not found")
                    conn.sendall(bytes(f"File not found", "utf-8"))
            else:
                logging.warning("Invalid message type " + data.decode("utf-8"))

    def handle_hello_message(self, data, node_ip):
        try:
            data_str = data.decode("utf-8")
            logging.info(f"Received HELLO message from {node_ip}")
            files_info = data_str[len("HELLO:"):].split('\n')
            logging.debug(f"Files Info: {files_info}")  
            for file_info in files_info:
                file_data = file_info.split(':')
                if len(file_data) == 4:
                    file_name, file_size, file_nBlocks, blocks_available = file_data
                    logging.debug(f"Node IP: {node_ip}, File: {file_name}, File_size: {file_size} Blocks: {blocks_available}, Total Blocks: {file_nBlocks}")
                    self.database.add_file(file_name, node_ip, blocks_available, file_nBlocks)
                else:
                    logging.warning(f"Invalid file info: {file_info}")
        except Exception as e:
            logging.error(f"Error in handle_hello_message: {e}")

    def handle_get_message(self, data, node_ip):
        try:
            data_str = data.decode("utf-8")
            logging.info(f"Received GET message from {node_ip}")
        
            file_name = data_str[len("GET:"):]
            file_info = self.database.get_all_files_info_string([file_name])
            logging.debug(f"Files Info: {file_info}")  
            
            return file_info
        except Exception as e:
            logging.error(f"Error in handle_get_message: {e}")
            
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
            # Handle the case where the size data is not a valid integer
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
    # Initialize the FS Track Protocol with the Tracker's host and port
    fs_track_protocol = FSTrackProtocol(HOST, PORT)

    # Start the server in a separate thread
    server_thread = threading.Thread(target=fs_track_protocol.start_server)
    server_thread.start()

    # Allow user interaction to view the database or exit
    while True:
        user_input = input(
            "Type 'view' to display the database in FS_Tracker or 'exit' to quit: ")
        if user_input.lower() == 'view':
            fs_track_protocol.tracker.database.view_database()
        elif user_input.lower() == 'exit':
            break
        else:
            print("Invalid command. Please try again.")
