from log import logger
from server.generic_master import GenericMasterThread, GenericMaster


class WorkMasterThread(GenericMasterThread):
    def __init__(self, *args, **kwargs):
        self.last_used_client_index = 0
        super(WorkMasterThread, self).__init__(*args, **kwargs)

    def new_connection(self, conn):
        self.push_filters_to_client(conn)

    def process_command(self, sock, command):
        if command == 'PING':
            self.send(sock, 'PONG')
        elif command == 'QUIT':
            self.send(sock, 'BYE')
            self.select_rlist.remove(sock)
            sock.close()
        elif command.startswith('HIT '):
            logger.info(command)
        else:
            self.send(sock, 'UNKNOWN COMMAND')

    def set_filters(self, filters):
        self.filters = filters
        self.push_filters_to_all_clients()

    def push_filters_to_all_clients(self):
        for c in self.select_rlist:
            self.push_filters_to_client(c)

    def push_filters_to_client(self, sock):
        for grp, x in self.filters.items():
            for f in x:
                self.send(sock, 'FILTER ADD %s %s' % (grp, f))

    def match_line(self, line):
        if len(self.client_socks) < 1:
            logger.error('No workers connected - unable to process line %s' % line)
        else:
            self.last_used_client_index += 1
            if self.last_used_client_index >= len(self.client_socks):
                self.last_used_client_index = 0

            self.send(self.client_socks[self.last_used_client_index], 'MATCH %s' % line)


class WorkerMaster(GenericMaster):
    master_thread_class = WorkMasterThread

    def prepare(self, *args, **kwargs):
        self.prepare_filters(kwargs.pop('filters', {}))

    def prepare_filters(self, filters):
        self.filters = {}
        for f in filters:
            grp, regex = f[:f.find(':')], f[f.find(':') + 1:]

            if grp not in self.filters.keys():
                self.filters[grp] = []
            self.filters[grp].append(regex)

    def pre_run(self):
        self.master_thread.set_filters(self.filters)

    def match_line(self, line):
        self.master_thread.match_line(line)
