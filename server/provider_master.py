from server.generic_master import GenericMasterThread, GenericMaster


class ProviderMasterThread(GenericMasterThread):
    def process_command(self, sock, command):
        self.worker_master.match_line(command)


class ProviderMaster(GenericMaster):
    master_thread_class = ProviderMasterThread

    def prepare(self, *args, **kwargs):
        self.worker_master = kwargs.pop('worker_master')

    def pre_run(self):
        self.master_thread.worker_master = self.worker_master
