import socket

class FS_Tracker:
    def __init__(self):
        self.database = {}  # Dicionário para armazenar informações de pacotes e arquivos
        self.server_address = ('localhost', 12345)  # Defina o endereço e a porta desejados
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)

    def register_package_info(self, data):
        data = data.decode()
        ip_address, files, blocks = data.split()
        self.database[ip_address] = {'files': files, 'blocks': blocks}

    def start_server(self):
        print("FS Tracker server is running...")
        while True:
            data, address = self.sock.recvfrom(4096)
            if data:
                self.register_package_info(data)

if __name__ == '__main__':
    tracker = FS_Tracker()
    tracker.start_server()
