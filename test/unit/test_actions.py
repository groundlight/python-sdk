import unittest

from groundlight import ExperimentalApi

# TODO change endpoint
gl = ExperimentalApi("https://api.dev.groundlight.ai/")


class TestActions(unittest.TestCase):
    def test_create_action(self):
        det = gl.get_or_create_detector("test_detector", "test_query")
        rule = gl.create_action(det, "test_rule", "EMAIL", "test@example.com")
        rule2 = gl.get_action(rule.id)
        self.assertTrue(rule == rule2)
        gl.delete_action(rule.id)
        self.assertRaises(Exception, gl.get_action, rule.id)

    def test_get_all_rules(self):
        det = gl.get_or_create_detector("test_detector", "test_query")
        gl.delete_all_rules()
        for i in range(100):
            _ = gl.create_action(det, f"test_rule_{i}", "EMAIL", "test@example.com")
        rules = gl.get_rules_list()
        self.assertEqual(len(rules), 100)
        gl.delete_all_rules()
        rules = gl.get_rules_list()
        self.assertEqual(len(rules), 0)
