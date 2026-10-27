import argparse
import socket
import struct


def parse_args():
    parser = argparse.ArgumentParser(description='Cliente TCP simple (conecta, manda un mensaje, cierra)')
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    parser.add_argument('mensaje', nargs='?', default='hola')
    parser.add_argument('--rst', action='store_true',
                        help='cierra de forma abrupta (RST) en vez de prolija (FIN)')
    return parser.parse_args()


def main():
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if args.rst:
        # SO_LINGER con tiempo 0: al cerrar, el kernel descarta lo pendiente
        # y manda RST en vez del cierre prolijo con FIN.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))

    sock.connect((args.host, args.port))
    sock.sendall(args.mensaje.encode('utf-8'))
    if not args.rst:
        reply = sock.recv(4096)
        print('Respuesta del servidor: {}'.format(reply))
    sock.close()


if __name__ == '__main__':
    main()
