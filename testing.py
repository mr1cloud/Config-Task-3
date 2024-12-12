import unittest
from main import load_xml, generate_config, evaluate_postfix, xml_to_dict

class TestStringMethods(unittest.TestCase):
    def test_load_xml(self):
        tree = load_xml('testing.xml')
        self.assertEqual(tree.tag, 'catalog')

    def test_evaluate_postfix(self):
        expression = ['a', 'b', '+']
        constants = {'a': 2, 'b': 5}
        result = evaluate_postfix(expression, constants)
        self.assertEqual(result, 7)

    def test_generate_config(self):
        tree = load_xml('testing.xml')
        data = xml_to_dict(tree)
        config = generate_config(data)
        self.assertEqual(config, """catalog = dict(
    constants = dict(
        constant --> 10,
        constant --> 20
    ),
    calculations = dict(
        calc = 30
    )
)""")
