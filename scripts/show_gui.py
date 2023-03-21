"""
@author: wangye(Wayne)
@license: Apache Licence
@file: show_gui.py
@time: 20230204
@contact: wang121ye@hotmail.com
@site:  wangyendt@github.com
@software: PyCharm

# code is far away from bugs.
"""

import collections
import sys

import matplotlib
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pywayne.data_structure import *

from config import DEBUG
from time_consumption_show import *

matplotlib.use("Qt5Agg")


class PlotDbgVars(FigureCanvas):
    def __init__(self, width=15, height=8, dpi=100, bk_color_and_alpha=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.subplots(1, 1)
        self.trash = []
        self.item = ''
        super(PlotDbgVars, self).__init__(self.fig)

    def plot_dbg_vars(self, data: np.ndarray, time_span: list):
        ts = data[:, 0].astype(float)
        ts -= time_span[0]
        ts /= 1e3
        consumption = data[:, 1]
        self.ax.cla()
        self.ax.plot(ts, consumption)
        self.ax.grid(True)
        self.ax.set_xlabel('time: (s)')
        self.ax.set_ylabel('running time: (ms)')
        self.ax.set_title(f'cur item: {self.item}')
        self.draw()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, data: dict, time_span: list, ct_tree: ConditionTree):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.F = PlotDbgVars()
        self.twAlgRules.clicked.connect(self.on_tree_clicked)
        self.hsCurFrame.valueChanged.connect(self.on_slider_value_changed)
        self.widget_root = None
        self.grid_layout = None
        self.data = data
        self.time_span = time_span
        self.ct_tree = ct_tree
        self.all_items = set()
        self.item_to_widget = dict()
        self.brothers_dict = collections.defaultdict(set)
        self.children_dict = collections.defaultdict(set)
        self.cur_time = 0
        self.cur_item = ''
        self.init()
        if DEBUG:
            print('*' * 80)
            print('brothers_dict:')
            for k, v in self.brothers_dict.items():
                print(k, v)
            print('*' * 80)
            print('children_dict:')
            for k, v in self.children_dict.items():
                print(k, v)
            print('*' * 80)

        self.teAlgLog.setTextColor(Qt.green)
        self.teAlgLog.setText(path)
        self.teAlgLog.setTextColor(Qt.black)

    def plot_debug_vars(self, data):
        if not self.grid_layout:
            self.grid_layout = QGridLayout(self.gbDebugPlt)
            self.grid_layout.addWidget(self.F, 0, 1)
        self.F.plot_dbg_vars(data, self.time_span)

    def init(self):
        self.twAlgRules.clear()
        self.twAlgRules.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.twAlgRules.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.twAlgRules.header().setStretchLastSection(False)
        self.twAlgRules.setColumnCount(1)
        self.twAlgRules.setHeaderLabels(['rule path'])
        self.widget_root = QTreeWidgetItem(self.twAlgRules)
        self.widget_root._tag = self.ct_tree.tag
        self.widget_root._attrib = self.ct_tree.attribute
        self.widget_root._text = self.ct_tree.text
        self.widget_root.setText(0, self.ct_tree.tag)

        def helper(_c_tree: ConditionTree, _widget_tree):
            if not _c_tree: return
            self.all_items.add(_c_tree.tag)
            self.children_dict[_c_tree.tag] = {c.tag for c in _c_tree.children}
            self.item_to_widget[_c_tree.tag] = _widget_tree
            for child in _c_tree.children:
                self.brothers_dict[child.tag] = self.children_dict[_c_tree.tag] ^ {child.tag}
                w_child = QTreeWidgetItem(_widget_tree)
                w_child._tag = child.tag
                w_child._attrib = child.attribute
                w_child._text = child.text
                text = child.tag + (': ' + child.text if child.text else '')
                w_child.setText(0, text)
                helper(child, w_child)

        helper(self.ct_tree, self.widget_root)
        self.twAlgRules.addTopLevelItem(self.widget_root)
        self.twAlgRules.expandAll()
        self.twAlgRules.show()
        self.cur_time = self.time_span[0]
        self.cur_item = ''

    def on_tree_clicked(self):
        if self.data is None or self.widget_root is None:
            return

        self.cur_item = self.twAlgRules.currentItem().text(0)
        self.F.item = self.cur_item
        self.plot_debug_vars(self.data[self.cur_item])
        self.update_view()

    def on_slider_value_changed(self):
        slider_value = self.hsCurFrame.value()
        self.cur_time = self.time_span[0] + (self.time_span[1] - self.time_span[0]) * slider_value // 99
        if not self.cur_item: return
        self.update_view()

    def update_view(self):
        def handle(item: str):
            res = collections.defaultdict(int)
            for it in {item} | self.brothers_dict[item]:
                seen.add(it)
                ts = self.data[it][:, 0]
                time_consumption = self.data[it][:, 1]
                right_side_idx = np.searchsorted(ts, self.cur_time, 'right')
                right_side_idx = min(right_side_idx, len(ts) - 1)
                if abs(self.cur_time - ts[right_side_idx]) <= 100:
                    res[it] = time_consumption[right_side_idx]
            mn, mx = min(res.values() or [0]), max(res.values() or [0])
            for k, v in res.items():
                color_red = np.array([255, 0, 0])
                color_green = np.array([0, 255, 0])
                w = v / mx  # ((v - mn) / (mx - mn)) if mx > mn else 1
                new_color = w * color_red + (1 - w) * color_green
                new_color = new_color.astype(int).clip(0, 255)
                self.item_to_widget[k].setBackground(0, QBrush(QColor(*new_color)))
                has_set_bg_color.add(k)

        self.teAlgLog.setTextColor(Qt.red)
        self.teAlgLog.append('=' * 20)
        self.teAlgLog.setTextColor(Qt.green)
        seen = set()
        has_set_bg_color = set()
        for item in self.all_items:
            if item not in seen:
                handle(item)
        total_num_of_nearby_children = 0
        total_elapsed_time = 0
        cur_elapsed_time = 0
        for it in self.children_dict[self.cur_item] | {self.cur_item}:
            ts = self.data[it][:, 0]
            time_consumption = self.data[it][:, 1]
            right_side_idx = np.searchsorted(ts, self.cur_time, 'right')
            right_side_idx = min(right_side_idx, len(ts) - 1)
            if abs(self.cur_time - ts[right_side_idx]) > 100:
                continue
            if it == self.cur_item:
                cur_elapsed_time = time_consumption[right_side_idx]
            else:
                total_num_of_nearby_children += 1
                total_elapsed_time += time_consumption[right_side_idx]
        self.teAlgLog.append(f'Cur item {self.cur_item} elapsed {cur_elapsed_time:.3f}ms')
        if len(self.children_dict[self.cur_item]) > 0:
            self.teAlgLog.append(f'{self.cur_item}\'s {total_num_of_nearby_children} children elapsed {total_elapsed_time:.3f}ms in total')
        self.teAlgLog.setTextColor(Qt.black)

        for item in self.all_items ^ has_set_bg_color:
            self.item_to_widget[item].setBackground(0, QBrush(Qt.transparent))

        # 增加指示线
        while self.F.trash:
            if self.F.trash[-1]:
                self.F.trash[-1][0].remove()
                del self.F.trash[-1][0]
            self.F.trash.pop()
        self.F.trash.append([self.F.ax.axvline((self.cur_time - self.time_span[0]) / 1e3, linestyle='--', linewidth=4, color='blue')])
        self.F.draw()


if __name__ == '__main__':
    from load_data import load_time_consumption_data
    from generate_function_tree import generate_tree_xml_from_log
    from config import PATH

    path = PATH if len(sys.argv) <= 1 else sys.argv[1]
    xml_path = '../tree_xml/function_tree.xml'
    generate_tree_xml_from_log(PATH, xml_path)
    xml = XmlIO(xml_path, xml_path)
    app = QApplication(sys.argv)
    data, time_span = load_time_consumption_data()
    ct_tree = xml.read()
    main = MainWindow(data, time_span, ct_tree)
    main.show()
    sys.exit(app.exec_())
