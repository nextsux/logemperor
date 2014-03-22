from worker.regex import Regex
import utils
from log import logger


class Worker(object):
    def __init__(self, server_at):
        self.server_at = server_at
        self.regex_worker = Regex()
        self.sock = utils.socket_connect_from_text(self.server_at)
        self.sock_f = self.sock.makefile(mode='r', encoding='UTF-8')

    def run(self):
        keep_running = True
        while keep_running:
            data = self.sock_f.readline()
            if data:
                data = data.strip()
                if data.startswith('FILTER ADD '):
                    data = data[11:].split(' ')
                    grp, regex = data[0], ' '.join(data[1:])
                    self.regex_worker.add_rule(grp, regex)
                elif data.startswith('MATCH '):
                    line = data[6:]
                    logger.debug('Matching: %s' % line)
                    for grp, r in self.regex_worker:
                        m = r.search(line)
                        if m:
                            logger.debug('Line "%s" matches group %s, host: %s' % (line, grp, m.groupdict().get('host', 'UNKNOWN')))
                            self.sock.send(('HIT %s %s\n' % (grp, m.groupdict().get('host', None))).encode('UTF-8'))
            else:
                keep_running = False
