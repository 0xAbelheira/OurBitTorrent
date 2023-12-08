import socket
import sys
import threading
import time


class Database:
    def __init__(self):
        self.dados = {"file_name": 3, "packets": -5, "ip": 1}
        self.lock = threading.Lock()


def funcao_servico1(socket, remetente, mensagem):
    for i in range(5):
        time.sleep(2)
        print(f"Recebi uma mensagem do {remetente}: {mensagem}\n")

    message = "Eu também :)\n\n"
    # Ou qualquer outro esquema de codificação que seja apropriado
    message_bytes = message.encode('utf-8')

    socket.sendto(message_bytes, remetente)


def funcao_servico2(socket, remetente, mensagem, db):
    with db.lock:
        del db.dados["coisas"]
        del db.dados["redes"]

    for i in range(5):
        time.sleep(2)
        print("SUCESIUM\n\n")

    socket.sendto(b"SUCESIUM\n\n", remetente)


def servico1(wg, db):
    try:
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_udp.bind((sys.argv[1], 0))

        print(f"Abri um socket e estou à escuta em {sys.argv[1]}\n\n")
        buffer = bytearray(1024)

        while True:
            data, remetente = socket_udp.recvfrom(1024)
            mensagem = data.decode('utf-8')

            threading.Thread(target=funcao_servico1, args=(
                socket_udp, remetente, mensagem)).start()

    except socket.error as err:
        print(f"Erro de socket: {err}")
        sys.exit(1)
    finally:
        wg.done()


def servico2(wg, db):
    try:
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_udp.bind((sys.argv[2], 0))

        print(f"Abri um socket e estou à escuta em {sys.argv[2]}\n\n")
        buffer = bytearray(1024)

        while True:
            data, remetente = socket_udp.recvfrom(1024)
            mensagem = data.decode('utf-8')

            threading.Thread(target=funcao_servico2, args=(
                socket_udp, remetente, mensagem, db)).start()

    except socket.error as err:
        print(f"Erro de socket: {err}")
        sys.exit(1)
    finally:
        wg.done()


def servico3(wg, db):
    try:
        while True:
            with db.lock:
                for key, value in db.dados.items():
                    time.sleep(2)
                    print(
                        f"Chave: {key} || Valor inicial: {value} || Valor final: {db.dados[key]}\n")
    finally:
        wg.done()


if __name__ == "__main__":
    wg = threading.Semaphore(3)
    db = Database()

    print("isto correu\n")

    threading.Thread(target=servico1, args=(wg, db)).start()
    threading.Thread(target=servico2, args=(wg, db)).start()
    threading.Thread(target=servico3, args=(wg, db)).start()

    while wg._value != 0:
        pass
