import socket
import pickle
import threading


class Tracker:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.database = {}

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            while True:
                conn, addr = server_socket.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        decoded_data = pickle.loads(data)
                        if decoded_data['type'] == 'hello':
                            self.handle_hello_message(decoded_data, addr[0])
                            conn.sendall(pickle.dumps(
                                {"message": "Hello received and processed"}))

    def handle_hello_message(self, data, node_ip):
        node_files = data['files']
        for file, file_info in node_files.items():
            if file not in self.database:
                self.database[file] = []
            self.database[file].append(
                {'node_ip_real': node_ip, 'node_ip_hardcoded': file_info['ip'], 'blocks_available': file_info['blocks_available'], 'total_blocks': file_info['total_blocks']})

    def view_database(self):
        for file, nodes in self.database.items():
            print(f"File: {file}")
            for node in nodes:
                print(
                    f"Node IP (real): {node['node_ip_real']}, Node IP (hardcoded): {node['node_ip_hardcoded']}, Blocks Available: {node['blocks_available']}, Total Blocks: {node['total_blocks']}")


if __name__ == "__main__":
    tracker = Tracker('localhost', 9888)

    server_thread = threading.Thread(target=tracker.start_server)
    server_thread.start()

    while True:
        user_input = input(
            "Digite 'view' para visualizar o dicionário no FS_Tracker ou 'exit' para sair: ")
        if user_input == 'view':
            tracker.view_database()
        elif user_input == 'exit':
            break
        else:
            print("Comando inválido. Por favor, tente novamente.")
