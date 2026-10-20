from mininet.net import Mininet
from mininet.node import Controller
from mininet.log import setLogLevel, info


def main():
    net = Mininet(controller=Controller)

    info('*** Creando nodos\n')
    net.addController('c0')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    s1 = net.addSwitch('s1')

    info('*** Creando enlaces\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    info('*** Iniciando red\n')
    net.start()

    info('*** Verificando conectividad entre h1 y h2\n')
    perdida = net.ping([h1, h2])

    info('*** Mensajes de prueba\n')
    info(h1.cmd('echo Hola desde h1'))
    info(h2.cmd('echo Hola desde h2'))
    info('*** Perdida de paquetes: {}%\n'.format(perdida))

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    main()
