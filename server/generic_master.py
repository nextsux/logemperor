import os
import threading
from select import select

from log import logger
import utils


class GenericMasterThread(threading.Thread):
    def __init__(self, sock):
        self.sock = sock
        self.keep_going = False
        self.select_rlist = []
        self.client_socks = []
        self.filters = {}
        threading.Thread.__init__(self)

    def run(self):
        self.select_rlist.append(self.sock)

        self.keep_going = True
        while self.keep_going:
            readable, writable, exceptional = select(self.select_rlist, [], self.select_rlist, 0.5)

            for sock in readable:
                if sock == self.sock:
                    # new connection
                    conn, client_address = self.sock.accept()
                    logger.info('New %s connection from %s' % (self.__class__.__name__, str(client_address)))
                    self.select_rlist.append(conn)
                    self.client_socks.append(conn)
                    self.new_connection(conn)
                else:
                    # new data from client
                    data = sock.recv(4096)
                    if not data:
                        # connection closed by client
                        try:
                            peer = sock.getpeername()
                        except:
                            peer = "UNKNOWN"
                        logger.info('%s connection %s closed' % (self.__class__.__name__, str(peer)))
                        sock.close()
                        self.select_rlist.remove(sock)
                        self.client_socks.remove(sock)
                    else:
                        try:
                            line = data.decode('UTF-8').strip()
                            if line != '':
                                logger.debug('%s got line: %s' % (self.__class__.__name__, line))
                                self.process_command(sock, line)
                        except UnicodeDecodeError:
                            logger.warn('%s recieved invalid data' % (self.__class__.__name__, ))

    def new_connection(self, conn):  # pragma: no cover
        pass

    def process_command(self, sock, command):  # pragma: no cover
        pass

    def send(self, sock, line):
        sock.send(bytes(line + "\n", 'UTF-8'))

    def request_stop(self):
        self.keep_going = False


class GenericMaster(object):
    master_thread_class = GenericMasterThread

    def __init__(self, listen_on, *args, **kwargs):
        self.sock_file = None
        self.master_thread = None

        self.prepare_sock(listen_on)
        self.prepare(*args, **kwargs)

    def prepare(*args, **kwargs):  # pragma: no cover
        pass

    def prepare_sock(self, listen_on):
        self.sock, self.sock_file = utils.socket_bind_from_text(listen_on)

    def run(self):
        self.master_thread = self.master_thread_class(self.sock)
        self.pre_run()
        self.master_thread.start()

    def pre_run(self):  # pragma: no cover
        pass

    def stop(self):
        if self.master_thread:
            self.master_thread.request_stop()
            self.master_thread.join()

        if self.sock_file:
            os.remove(self.sock_file)
        self.sock.close()
