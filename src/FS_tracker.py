import socket
import pickle
from Database import Database
import threading

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


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
        """
        Initializes the Tracker object with the given host and port.
        Creates an empty database to store node information.
        """
        self.host = host
        self.port = port
        self.database = Database()

    def start_server(self):
        """
        Starts the server on the specified host and port.
        Listen for incoming connections and handle the 'hello' message from nodes.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            while True:
                conn, addr = server_socket.accept()
                with conn:
                    print(f"\nConnected by {addr}")
                    msg = b""
                    data = conn.recv(10)
                    
                    if data:
                        decoded_data = pickle.loads(data)
                        if decoded_data['type'] == 'HELLO':
                            self.handle_hello_message(decoded_data, addr[0])
                            conn.sendall(pickle.dumps(
                                {"message": "Data received and processed"}))
                        if decoded_data['type'] == 'GET':
                            conn.sendall(conn.sendall(pickle.dumps(
                                {"message": "Response of type:GET not yet implemented"})))

    def handle_hello_message(self, data, node_ip):
        """
        Handle the 'hello' message from nodes.
        Update node information in the database if the node already exists; otherwise, add a new node entry.
        """
        node_files = data['files']
        for file, file_info in node_files.items():
            self.database.add_file(
                file, node_ip, file_info['blocks_available'], file_info['total_blocks'])

    def view_database(self):
        self.database.view_database()


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
        if user_input == 'view':  # Colocar toUpper
            fs_track_protocol.view_database()
        elif user_input == 'exit':
            break
        else:
            print("Invalid command. Please try again.")
