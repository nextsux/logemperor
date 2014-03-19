import unittest
from unittest.mock import patch
import socket
import tempfile
import os

import server.worker_master
from server.worker_master import WorkerMaster
import utils


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

    @patch.object(server.worker_master.logger, 'info')
    @prepare_sockfile
    def test_commands(self, mock_logger_info, sock_file):
        wm = WorkerMaster('sock://%s' % sock_file)
        wm.run()

        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_file)

            s.send(bytes('PING\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'PONG')

            s.send(bytes('FOOBAR\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'UNKNOWN COMMAND')

            mock_logger_info.reset_mock()
            s.send(bytes('HIT grp 1.1.1.1\n', 'UTF-8'))
            self.assertEqual(s.recv(1024).decode('UTF-8').strip(), 'BULLSEYE')
            mock_logger_info.assert_called_once_with('HIT grp 1.1.1.1')

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

    @prepare_sockfile
    def test_filters(self, sock_file):
        wm = WorkerMaster('sock://%s' % sock_file, filters=['grp1:aaa', 'grp1:bbb', 'grp2:ccc'])
        wm.run()

        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_file)
            f = s.makefile('r')

            self.assertEqual(sorted([f.readline().strip() for _ in range(3)]), ['FILTER ADD grp1 aaa', 'FILTER ADD grp1 bbb', 'FILTER ADD grp2 ccc'])

            f.close()
            s.close()
        finally:
            wm.stop()

    @patch.object(server.worker_master.logger, 'error')
    @prepare_sockfile
    def test_match_line(self, mock_logger_error, sock_file):
        wm = WorkerMaster('sock://%s' % sock_file, filters=['grp1:aaa', 'grp1:bbb', 'grp2:ccc'])
        wm.run()

        try:
            wm.match_line('test line')
            mock_logger_error.assert_called_once_with('No workers connected - unable to process line "test line"')

            s1 = utils.socket_connect_from_text("sock://%s" % sock_file)
            f1 = s1.makefile('r')
            # ignore filter definitions
            for _ in range(3):
                f1.readline().strip()

            s2 = utils.socket_connect_from_text("sock://%s" % sock_file)
            f2 = s2.makefile('r')
            # ignore filter definitions
            for _ in range(3):
                f2.readline().strip()

            wm.match_line('test line2')
            wm.match_line('test line3')

            l1 = f1.readline().strip()
            l2 = f2.readline().strip()
            self.assertIn(l1, ('MATCH test line2', 'MATCH test line3', ))
            self.assertIn(l2, ('MATCH test line2', 'MATCH test line3', ))
            self.assertNotEqual(l1, l2)

            f1.close()
            s1.close()
            f2.close()
            s2.close()
        finally:
            wm.stop()
