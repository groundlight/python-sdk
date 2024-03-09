import unittest

from groundlight import ExperimentalApi



class TestActions(unittest.TestCase):
    def setUp(self) -> None:
        self.gl = ExperimentalApi()
        return super().setUp()

    def test_create_action(self):
        det = self.gl.get_or_create_detector("test_detector", "test_query")
        rule = self.gl.create_action(det, "test_rule", "EMAIL", "test@example.com")
        rule2 = self.gl.get_action(rule.id)
        self.assertTrue(rule == rule2)
        self.gl.delete_action(rule.id)
        self.assertRaises(Exception, self.gl.get_action, rule.id)

    def test_get_all_rules(self):
        det = self.gl.get_or_create_detector("test_detector", "test_query")
        self.gl.delete_all_rules()
        for i in range(100):
            _ = self.gl.create_action(det, f"test_rule_{i}", "EMAIL", "test@example.com")
        rules = self.gl.get_rules_list()
        self.assertEqual(len(rules), 100)
        self.gl.delete_all_rules()
        rules = self.gl.get_rules_list()
        self.assertEqual(len(rules), 0)
