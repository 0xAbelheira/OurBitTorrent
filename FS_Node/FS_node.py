import socket
import pickle


class Node:
    def __init__(self, host, port, tracker_host, tracker_port):
        self.host = host
        self.port = port
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.files = {
            'example_file1.txt': {
                'ip': '192.168.0.2',
                'blocks_available': [1, 2, 3],
                'total_blocks': 5
            },
            'example_file2.txt': {
                'ip': '192.168.0.1',
                'blocks_available': [2, 4, 5, 6],
                'total_blocks': 6
            },
            'example_file3.txt': {
                'ip': '192.168.0.2',
                'blocks_available': [7, 8, 9],
                'total_blocks': 9
            }
        }

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.connect((self.tracker_host, self.tracker_port))
            message = {'type': 'hello', 'files': self.files}
            node_socket.sendall(pickle.dumps(message))
            data = node_socket.recv(1024)
            if data:
                response = pickle.loads(data)
                print(response['message'])


if __name__ == "__main__":
    node = Node('localhost', 9999, 'localhost', 9888)
    node.start()
