import argparse, re
import xml.etree.ElementTree as ElementTree

OPERATIONS = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    'max': lambda *args: max(args),
    'mod': lambda x, y: x % y
}

def main():
    parser = argparse.ArgumentParser(description="Transform XML to custom configuration language.")
    parser.add_argument('--input', required=True, help="Input file path.")
    parser.add_argument('--output', required=True, help="Output file path.")
    args = parser.parse_args()