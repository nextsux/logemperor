import unittest
from unittest.mock import patch

import logging
import log


class TestLog(unittest.TestCase):
    @patch.object(log.logging.Logger, 'setLevel')
    @patch.object(log.logging.Logger, 'addHandler')
    def test_log_init(self, mock_add_handler, mock_set_logging):
        log.init('DEBUG')
        mock_set_logging.assert_called_once_with(logging.DEBUG)
        mock_add_handler.assert_called_once()
