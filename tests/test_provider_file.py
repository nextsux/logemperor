import unittest
import tempfile
import os

from provider.file import File


class TestProviderFile(unittest.TestCase):
    def setUp(self):
        self.logfd, self.logfile = tempfile.mkstemp()
        self.provider = File(self.logfile)

    def tearDown(self):
        os.close(self.logfd)
        os.remove(self.logfile)

    def test_empty(self):
        r = self.provider.get_next()
        self.assertEqual(r, '')

    def test_get(self):
        with open(self.logfile, 'a') as f:
            f.write('test_line1\n')
        self.assertEqual(self.provider.get_next(), 'test_line1')

    def test_get_multiple(self):
        with open(self.logfile, 'a') as f:
            f.write('test_line2\n')
            f.write('test_line3\n')

        self.assertEqual(self.provider.get_next(), 'test_line2')
        self.assertEqual(self.provider.get_next(), 'test_line3')

    def test_trim(self):
        with open(self.logfile, 'a') as f:
            f.write('test_line4\n')
            f.write('test_line5\n')
        self.assertEqual(self.provider.get_next(), 'test_line4')
        self.assertEqual(self.provider.get_next(), 'test_line5')

        with open(self.logfile, 'w') as f:
            f.write('test_line6\n')

        self.assertEqual(self.provider.get_next(), 'test_line6')

    def test_logrotate(self):
        with open(self.logfile, 'a') as f:
            f.write('test_line7\n')
            f.flush()
            self.assertEqual(self.provider.get_next(), 'test_line7')
            f.write('test_line8\n')

        os.close(self.logfd)
        os.remove(self.logfile)
        self.logfd = open(self.logfile, 'w').fileno()

        with open(self.logfile, 'w') as f:
            f.write('test_line9\n')

        self.assertEqual(self.provider.get_next(), 'test_line8')
        self.assertEqual(self.provider.get_next(), 'test_line9')
