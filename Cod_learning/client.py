import socket
import pickle

HEADERSIZE = 15

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))   #Normalmente nao é usado socket.gethostname(),temos de conectar a um public ip

while True:
    
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(20) #Utilizamos 20 para receber mais um bocado do que o header
        if new_msg:
            print(f"new message lenght: {msg[:HEADERSIZE]}")
            msglen = int(msg[:HEADERSIZE]) #Noutra linguagem, seria preciso retirar os espacos em "branco" deixados pelo header
            new_msg = False

        full_msg += msg

        if len(full_msg)-HEADERSIZE == msglen:
            print("full msg recvd")
            print(full_msg[HEADERSIZE:])
            
            d = pickle.loads(full_msg[HEADERSIZE:])
            print(d)
            
            new_msg = True
            full_msg = b''
    
    print(full_msg)
