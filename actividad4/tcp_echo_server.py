import socket
import sys


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', port))
    srv.listen(5)
    print('Escuchando en el puerto {}...'.format(port))
    while True:
        conn, addr = srv.accept()
        print('Conexion aceptada desde {}'.format(addr))
        data = conn.recv(4096)
        if data:
            conn.sendall(data)
        conn.close()


if __name__ == '__main__':
    main()
