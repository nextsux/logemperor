import unittest
import socket
import tempfile
import os

from server.worker_master import WorkerMaster


def prepare_sockfile(func):
    def test_wrapper(*args, **kwargs):
        d = tempfile.mkdtemp()
        sock_file = os.path.join(d, 'test.sock')
        kwargs.update({
            'sock_file': sock_file
        })
        try:
            r = func(*args, **kwargs)
        finally:
            os.rmdir(d)

        return r
    return test_wrapper


class TestWorkerMaster(unittest.TestCase):
    def test_listen_tcp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wm = WorkerMaster('tcp://0.0.0.0:4432')
        wm.run()

        s.connect(('127.0.0.1', 4432))
        s.close()
        wm.stop()

    def test_listen_tcp6(self):
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        wm = WorkerMaster('tcp6://[::1]:4432')
        wm.run()

        s.connect(('::1', 4432))
        s.close()
        wm.stop()

    @prepare_sockfile
    def test_listen_sock(self, sock_file):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        wm = WorkerMaster('sock://%s' % sock_file)
        wm.run()

        s.connect(sock_file)
        s.close()
        wm.stop()

    def test_listen_unknown(self):
        with self.assertRaises(NotImplementedError):
            WorkerMaster('unknown://whatever')

    @prepare_sockfile
    def test_commands(self, sock_file):
        wm = WorkerMaster('sock://%s' % sock_file)
        wm.run()

        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_file)

            s.send(bytes('PING\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'PONG')

            s.send(bytes('FOOBAR\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'UNKNOWN COMMAND')

            s.send(bytes('QUIT\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'BYE')

            with self.assertRaises(BrokenPipeError):
                s.send(bytes('ANYTHING\n', 'UTF-8'))
            s.close()
        finally:
            wm.stop()

    @prepare_sockfile
    def test_client_close_connection(self, sock_file):
        wm = WorkerMaster('sock://%s' % sock_file)
        wm.run()

        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_file)

            s.send(bytes('PING\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'PONG')
            s.close()
        finally:
            wm.stop()
