import socket
import time
import pickle

HEADERSIZE = 15

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)

while True:
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established!")

    d = {1: "Hey", 2: "There"}
    msg = pickle.dumps(d)

    # 10 is the header lenght (discutir este valor... deve ser fixo por alguma razao)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf-8") + msg

    clientsocket.send(msg)
