"""
@author: wangye(Wayne)
@license: Apache Licence
@file: main.py
@time: 20230201
@contact: wang121ye@hotmail.com
@site:  wangyendt@github.com
@software: PyCharm

# code is far away from bugs.
"""
import collections

from pywayne.data_structure import *


def generate_tree_xml_from_log():
    path = '/Users/wayne/Documents/work/project/20230116 slam数据采集和耗时统计/running_time/273393920.txt'
    with open(path, 'r') as f:
        lines = f.readlines()
        seen = set()
        paths = []
        edges = collections.defaultdict(list)
        root = 'TrackMonocular'
        tree = ConditionTree(root)

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
        print(edges)

        def helper(parent: str):
            children = edges[parent]
            for child in children:
                paths[child] = paths[parent][:]
                paths[child].append(child)
                helper(child)

        paths = collections.defaultdict(list)
        helper(root)
        ct_paths = lambda x: {'tag': x, 'attrib': '', 'text': ''}
        [tree.append_by_path(list(map(ct_paths, p))) for p in paths.values()]
        xml = XmlIO(file_write='config.xml')
        xml.write(root, tree)


def read_tree_xml():
    xml = XmlIO('config.xml', 'config.xml')
    ct = xml.read()
    print(ct.tag)
    print(ct.children[0].tag)


def main():
    # generate_tree_xml_from_log()
    read_tree_xml()


if __name__ == '__main__':
    main()
