import socket
import sys


def main():
    try:
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_udp.bind(("", 0))

        # Porta 12345, substitua pela porta desejada
        endereco = (sys.argv[1], 12345)

        socket_udp.sendto(b"Adoro Redes :)", endereco)

        buffer, servidor = socket_udp.recvfrom(1024)

        print(
            f"Recebi resposta do servidor {servidor}: {buffer.decode('utf-8')}")

    except socket.error as err:
        print(f"Erro de socket: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()