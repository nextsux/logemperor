import unittest
import socket
import tempfile
import os

from server.worker_master import WorkerMaster


class TestWorkerMaster(unittest.TestCase):
    def test_listen_tcp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wm = WorkerMaster('tcp://0.0.0.0:4432')
        s.connect(('127.0.0.1', 4432))
        s.close()
        wm.stop()

    def test_listen_tcp6(self):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        wm = WorkerMaster('tcp6://[::1]:4432')
        s.connect(('::1', 4432))
        s.close()
        wm.stop()

    def test_listen_sock(self):
        d = tempfile.mkdtemp()
        sock_file = os.path.join(d, 'test.sock')

        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        wm = WorkerMaster('sock://%s' % sock_file)
        s.connect(sock_file)
        s.close()
        wm.stop()

        os.rmdir(d)

    def test_listen_unknown(self):
        with self.assertRaises(NotImplementedError):
            WorkerMaster('unknown://whatever')
