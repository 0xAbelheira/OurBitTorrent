import socket
import pickle

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
HEADERSIZE = 15

class FSTransferProtocol:
    """
    Class for implementing the FS Transfer Protocol for communication between nodes.
    """

    def __init__(self, host, port, tracker_host, tracker_port):
        self.node = Node(host, port, tracker_host, tracker_port)

    def start(self):
        self.node.start()


class Node:
    def __init__(self, host, port, tracker_host, tracker_port):
        self.host = host
        self.port = port
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.files = {
            'example_file1.txt': {
                'ip': '192.168.0.2',
                'blocks_available': [1, 2, 3, 4, 5],
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
            
            
if __name__ == "__main__":
    # Initialize the FS Transfer Protocol with the Node's host, port, tracker's host, and port
    fs_transfer_protocol = FSTransferProtocol('localhost', 9999, HOST, PORT)
    fs_transfer_protocol.start()
