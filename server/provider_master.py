from server.generic_master import GenericMasterThread, GenericMaster


class ProviderMasterThread(GenericMasterThread):
    pass


class ProviderMaster(GenericMaster):
    master_thread_class = ProviderMasterThread
