"""
@author: wangye(Wayne)
@license: Apache Licence
@file: generate_function_tree.py
@time: 20230201
@contact: wang121ye@hotmail.com
@site:  wangyendt@github.com
@software: PyCharm

# code is far away from bugs.
"""
import collections
from config import PATH
from pywayne.data_structure import *


def generate_tree_xml_from_log(log_path, xml_path):
    with open(log_path, 'r') as f:
        lines = f.readlines()
        seen = set()
        paths = []
        edges = collections.defaultdict(list)
        root = ''

        for i, line in enumerate(lines[1:]):
            line = line.rstrip()
            timestamp, node, consumption = line.split(',')
            if node not in seen:
                items = node.split('_')
                if len(items) == 2:
                    root = items[1]
                elif len(items) == 3:
                    edges[items[1]].append(items[2])
                else:
                    raise ValueError(f'len(items) should be 2 or 3, rather than {len(items)}')
                seen.add(node)

        def helper(parent: str):
            children = edges[parent]
            for child in children:
                paths[child] = paths[parent][:]
                paths[child].append(child)
                helper(child)

        paths = collections.defaultdict(list)
        helper(root)
        tree = ConditionTree(root)
        ct_paths = lambda x: {'tag': x, 'attrib': '', 'text': ''}
        [tree.append_by_path(list(map(ct_paths, p))) for p in paths.values()]
        xml = XmlIO(file_write=xml_path)
        xml.write(root, tree)


def read_tree_xml():
    xml = XmlIO('function_tree.xml', 'function_tree.xml')
    ct = xml.read()
    # print(ct.tag)
    # print(ct.children[0].tag)
    # print(ct.children[0].children[0].children[0].children[0].tag)


def main():
    generate_tree_xml_from_log()
    read_tree_xml()


if __name__ == '__main__':
    main()
