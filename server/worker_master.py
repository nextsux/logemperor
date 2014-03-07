import socket
import os


class WorkerMaster(object):
    def __init__(self, listen_on):
        self.sock_file = None

        if listen_on.startswith('tcp://'):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            l = listen_on[6:].split(':')
            self.sock.bind((l[0], int(l[1])))
        elif listen_on.startswith('tcp6://'):
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            l = listen_on[7:]
            port_sep = l.rfind(':')
            addr, port = l[:port_sep].strip('[]'), int(l[port_sep + 1:])
            self.sock.bind((addr, port))
        elif listen_on.startswith('sock://'):
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock_file = listen_on[7:]
            self.sock.bind(self.sock_file)
        else:
            raise NotImplementedError('Unknown listen type')

        self.sock.listen(1)

    def stop(self):
        if self.sock_file:
            os.remove(self.sock_file)
        self.sock.close()
