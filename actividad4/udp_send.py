import sys
import socket


def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    message = sys.argv[3] if len(sys.argv) > 3 else 'hola'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('utf-8'), (host, port))
    sock.close()
    print('Datagrama UDP enviado a {}:{}'.format(host, port))


if __name__ == '__main__':
    main()
