from systemd import journal


class Journald(object):
    def __init__(self, matches={}):
        self.j = journal.Reader()
        for k, v in matches.items():
            self.j.add_match("%s=%s" % (k, v))
        self.j.seek_tail()
        self.j.get_previous()

    def get_data(self):
        e = self.j.get_next()
        return e.get('MESSAGE', '').strip()
