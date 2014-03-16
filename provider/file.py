import os
import io
import time

from log import logger


class File(object):
    def __init__(self, logfile):
        self.logfile = logfile
        self.log = None
        self.loginode = None

    def open(self, seek_to_end=True):
        if not self.log:
            self.log = open(self.logfile, 'r')
            self.loginode = os.fstat(self.log.fileno()).st_ino
            if seek_to_end:
                self.log.seek(0, io.SEEK_END)

    def close(self):
        if self.log:
            self.log.close()
            self.log = None

    def reopen(self):
        self.close()
        self.open(seek_to_end=False)

    def get_next(self):
        self.open()

        l = self.log.readline()
        if not l:
            if self.log.tell() > os.fstat(self.log.fileno()).st_size:
                self.log.seek(0)
                l = self.log.readline()
                logger.info('Log file %s was trimmed, seeked to beginning' % self.logfile)
            elif os.stat(self.logfile).st_ino != self.loginode:
                logger.info('Log file %s was re-created, reopened' % self.logfile)
                self.reopen()
                l = self.log.readline()
            else:
                time.sleep(0.5)

        return l.strip()
