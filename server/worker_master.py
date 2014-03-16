import socket
import os
import threading
from log import logger
from select import select


class WorkMasterThread(threading.Thread):
    def __init__(self, sock):
        self.sock = sock
        self.keep_going = False
        self.select_rlist = []
        self.filters = {}
        threading.Thread.__init__(self)

    def run(self):
        self.select_rlist.append(self.sock)

        self.keep_going = True
        while self.keep_going:
            readable, writable, exceptional = select(self.select_rlist, [], self.select_rlist, 0.5)

            for sock in readable:
                if sock == self.sock:
                    # new connection from worker
                    conn, client_address = self.sock.accept()
                    logger.info('New worker connection from %s:%i' % (client_address[0], client_address[1]))
                    self.select_rlist.append(conn)
                    self.push_filters_to_client(conn)
                else:
                    # new data from client
                    data = sock.recv(4096)
                    if not data:
                        # connection closed by client
                        sock.close()
                        self.select_rlist.remove(sock)
                    else:
                        try:
                            self.process_command(sock, data.decode('UTF-8').strip())
                        except UnicodeDecodeError:
                            logger.warn('Recieved invalid data')

    def request_stop(self):
        self.keep_going = False

    def process_command(self, sock, command):
        if command == 'PING':
            self.send_response(sock, 'PONG')
        elif command == 'QUIT':
            self.send_response(sock, 'BYE')
            self.select_rlist.remove(sock)
            sock.close()
        else:
            self.send_response(sock, 'UNKNOWN COMMAND')

    def send_response(self, sock, response):
        sock.send(bytes(response + "\n", 'UTF-8'))

    def set_filters(self, filters):
        self.filters = filters
        self.push_filters_to_all_clients()

    def push_filters_to_all_clients(self):
        for c in self.select_rlist:
            self.push_filters_to_client(c)

    def push_filters_to_client(self, sock):
        self.send_response(sock, 'FILTER CLEAR')
        for grp, x in self.filters.items():
            for f in x:
                self.send_response(sock, 'FILTER ADD %s %s' % (grp, x))


class WorkerMaster(object):
    def __init__(self, listen_on, filters=None):
        self.sock_file = None
        self.master_thread = None

        self.prepare_sock(listen_on)
        self.prepare_filters(filters if filters is not None else [])

    def prepare_sock(self, listen_on):
        if listen_on.startswith('tcp://'):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            l = listen_on[6:].split(':')
            self.sock.bind((l[0], int(l[1])))
        elif listen_on.startswith('tcp6://'):
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

        self.sock.setblocking(0)
        self.sock.listen(5)

    def prepare_filters(self, filters):
        self.filters = {}
        for f in filters:
            grp, regex = f[:f.find(':')], f[f.find(':') + 1:]

            if grp not in self.filters.keys():
                self.filters[grp] = []
            self.filters[grp].append(regex)

    def run(self):
        self.master_thread = WorkMasterThread(self.sock)
        self.master_thread.set_filters(self.filters)
        self.master_thread.start()

    def stop(self):
        if self.master_thread:
            self.master_thread.request_stop()
            self.master_thread.join()

        if self.sock_file:
            os.remove(self.sock_file)
        self.sock.close()
