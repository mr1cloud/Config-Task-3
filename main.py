import argparse, re
import xml.etree.ElementTree as ElementTree


OPERATIONS = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    'max': lambda *args: max(args),
    'mod': lambda x, y: x % y
}


def evaluate_postfix(expression, constants):
    stack = []
    for token in expression:
        if token in constants:
            stack.append(constants[token])
        elif token in OPERATIONS:
            if token == 'max':
                args = [stack.pop() for _ in range(len(stack))]
                stack.append(OPERATIONS[token](*args))
            else:
                y, x = stack.pop(), stack.pop()
                stack.append(OPERATIONS[token](x, y))
        else:
            stack.append(float(token))
    return stack[0]


def load_xml(file_path: str) -> ElementTree.Element:
    parser = ElementTree.XMLParser(target=ElementTree.TreeBuilder(insert_comments=True))
    tree = ElementTree.parse(file_path, parser)
    root = tree.getroot()
    return root


def xml_to_dict(node: ElementTree.Element) -> dict:
    def parse_comments_and_children(element):
        items = []
        for child in element:
            if child.tag is ElementTree.Comment:
                items.append({"comment": child.text.strip() if child.text else ""})
            else:
                items.append(xml_to_dict(child))
        return items

    value = node.text.strip() if node.text and node.text.strip() else ''

    if value:
        if value and value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass

    result = {
        "tag": node.tag,
        "attributes": node.attrib,
        "value": value,
        "content": parse_comments_and_children(node)
    }

    return result


def generate_config(data: dict) -> str:
    constants = {}

    def format_value(value):
        if isinstance(value, str):
            return f"[[{value}]]"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, dict):
            return generate_dict(value)
        else:
            raise ValueError("Unsupported value type")

    def generate_dict(data: dict) -> str:
        entries = []
        for key, value in data.items():
            entries.append(f"    {key} = {format_value(value)}")
        buffer = ',\n'.join(entries)
        return f"dict(\n{buffer}\n)"

    def process_node(node):
        lines = []
        if "comment" in node:
            comment = node["comment"]
            if "\n" in comment:
                lines.append(f"<!--\n{comment}\n-->".replace("\n", "\n    "))
            else:
                lines.append(f"|| {comment}")

        tag = node.get("tag")
        attributes = node.get("attributes", {})
        value = node.get("value")
        content = node.get("content", [])

        if attributes:
            attr_dict = generate_dict(attributes)
            lines.append(f"{tag} = {attr_dict}")
        if value:
            if type(value) in (int, float):
                if tag == 'constant':
                    constants[node['attributes']['name']] = value
                    lines.append(f"{tag} --> {format_value(value)}")
                else:
                    lines.append(f"{tag} = {format_value(value)}")
            else:
                if '@{' not in value:
                    lines.append(f"{tag} = {format_value(value)}")
                if '@{' in value:
                    expression = value.strip('@{}').split()
                    if expression[-1] in OPERATIONS:
                        result = evaluate_postfix(expression, constants)
                        lines.append(f"{tag} = {result}")

        for child in content:
            lines.append(process_node(child))

        return "\n".join(lines)

    return process_node(data)


def main():
    parser = argparse.ArgumentParser(description="Transform XML to custom configuration language.")
    parser.add_argument('--input', required=True, help="Input file path.")
    parser.add_argument('--output', required=True, help="Output file path.")
    args = parser.parse_args()

    root = load_xml(args.input)
    data = xml_to_dict(root)
    print(data)
    config = generate_config(data)
    with open(args.output, "w") as file:
        file.write(config)


if __name__ == '__main__':
    main()
