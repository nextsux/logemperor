import re


class Regex(object):
    def __init__(self):
        self.rules = {}

    def get_rules_all(self):
        return {
            x: [
                y.pattern for y in self.rules[x]
            ] for x in self.rules.keys()
        }

    def compiled_regex_generator(self):
        for grp, regexes in self.rules.items():
            for r in regexes:
                yield r

    def get_rules(self, grp):
        try:
            return [x.pattern for x in self.rules[grp]]
        except KeyError:
            return []

    def add_rule(self, grp, regex):
        if regex not in self.get_rules(grp):
            self.rules[grp] = self.rules.get(grp, []) + [re.compile(regex), ]

    def remove_rule(self, grp, regex):
        newrules = [x for x in self.rules[grp] if x.pattern != regex]
        if not (len(newrules) < len(self.rules[grp])):
            raise KeyError()
        self.rules[grp] = newrules

    def remove_rules(self, grp):
        del self.rules[grp]

    def remove_rules_all(self):
        self.rules = {}

    def __iter__(self):
        self.regex_iter = self.compiled_regex_generator()
        return self

    def __next__(self):
        return next(self.regex_iter)
