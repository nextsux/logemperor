from server.generic_master import GenericMasterThread, GenericMaster


class WorkMasterThread(GenericMasterThread):
    def new_connection(self, conn):
        self.push_filters_to_client(conn)

    def process_command(self, sock, command):
        if command == 'PING':
            self.send_response(sock, 'PONG')
        elif command == 'QUIT':
            self.send_response(sock, 'BYE')
            self.select_rlist.remove(sock)
            sock.close()
        else:
            self.send_response(sock, 'UNKNOWN COMMAND')

    def set_filters(self, filters):
        self.filters = filters
        self.push_filters_to_all_clients()

    def push_filters_to_all_clients(self):
        for c in self.select_rlist:
            self.push_filters_to_client(c)

    def push_filters_to_client(self, sock):
        for grp, x in self.filters.items():
            for f in x:
                self.send_response(sock, 'FILTER ADD %s %s' % (grp, f))


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
