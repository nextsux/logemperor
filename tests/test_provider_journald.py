import unittest
import time
from systemd import journal

from provider.journald import Journald


class TestProviderJournald(unittest.TestCase):
    def setUp(self):
        self.provider = Journald({'SYSLOG_IDENTIFIER': 'logemperor-test'})

    def log_message(self, msg):
        journal.send(msg, SYSLOG_IDENTIFIER='logemperor-test')
        # wait for log message to process
        time.sleep(0.05)

    def test_get_data_empty(self):
        self.assertEqual(self.provider.get_data(), '')

    def test_get_data(self):
        self.log_message('test_line1')
        self.assertEqual(self.provider.get_data(), 'test_line1')

    def test_get_data_buffer(self):
        self.log_message('test_line2')
        self.log_message('test_line3')

        self.assertEqual(self.provider.get_data(), 'test_line2')
        self.assertEqual(self.provider.get_data(), 'test_line3')
