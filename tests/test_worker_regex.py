import unittest

from worker.regex import Regex


class TestWorkerRegex(unittest.TestCase):
    def setUp(self):
        self.w = Regex()

    def test_rules_mng(self):
        self.assertEqual(self.w.get_rules_all(), {})

        self.w.add_rule('test1', '^rule1$')
        self.w.add_rule('test1', '^rule2$')
        self.w.add_rule('test1', '^rule3$')
        self.w.add_rule('test2', '^rule4$')
        self.w.add_rule('test2', '^rule5$')
        self.w.add_rule('test2', '^rule5$')
        self.w.add_rule('test2', '^rule5$')

        self.assertEqual(self.w.get_rules_all(), {
            'test1': ['^rule1$', '^rule2$', '^rule3$'],
            'test2': ['^rule4$', '^rule5$'],
        })

        self.assertEqual(self.w.get_rules('test2'), ['^rule4$', '^rule5$'])
        self.assertEqual(self.w.get_rules('not_defined'), [])

        self.w.remove_rule('test2', '^rule4$')
        self.assertEqual(self.w.get_rules('test2'), ['^rule5$'])

        self.w.remove_rules('test1')
        self.assertEqual(self.w.get_rules_all(), {
            'test2': ['^rule5$', ],
        })

        with self.assertRaises(KeyError):
            self.w.remove_rules('not_defined')

        with self.assertRaises(KeyError):
            self.w.remove_rule('test2', '^rule4$')

        self.w.remove_rules_all()
        self.assertEqual(self.w.get_rules_all(), {})

    def test_compiled_regex_generator(self):
        regexes = [x for x in self.w.compiled_regex_generator()]
        self.assertEqual(regexes, [])

        self.w.add_rule('test1', '^rule1$')
        self.w.add_rule('test2', '^rule2$')
        self.w.add_rule('test2', '^rule3$')

        regexes = [x[1].pattern for x in self.w.compiled_regex_generator()]
        self.assertEqual(sorted(regexes), sorted(['^rule1$', '^rule2$', '^rule3$', ]))

    def test_iter(self):
        self.w.add_rule('test1', '^rule1$')
        self.w.add_rule('test2', '^rule2$')
        self.w.add_rule('test2', '^rule3$')

        patterns = []
        for x in self.w:
            patterns.append(x[1].pattern)

        self.assertEqual(sorted(patterns), sorted(['^rule1$', '^rule2$', '^rule3$', ]))
