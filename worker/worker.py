from worker.regex import Regex
import utils


class Worker(object):
    def __init__(self, server_at):
        self.server_at = server_at
        self.regex_worker = Regex()
        self.sock = utils.socket_connect_from_text(self.server_at)
        self.sock_f = self.sock.makefile(mode='rw', encoding='UTF-8')

    def run(self):
        while True:
            data = self.sock_f.readline().strip()
            if data.startswith('FILTER ADD '):
                data = data[11:].split(' ')
                grp, regex = data[0], ' '.join(data[1:])
                self.regex_worker.add_rule(grp, regex)
