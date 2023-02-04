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
import re
import sys

import matplotlib
import pandas as pd
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pywayne.data_structure import *

from time_consumtion_show import *

matplotlib.use("Qt5Agg")


class PlotDbgVars(FigureCanvas):
    def __init__(self, width=15, height=8, dpi=100, bk_color_and_alpha=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax_acc = self.fig.subplots(1, 1)
        self.ax_prs = self.ax_acc.twinx()
        super(PlotDbgVars, self).__init__(self.fig)

    def plot_dbg_vars(self, df: pd.DataFrame, frame: int):
        data = df.loc[frame]
        self.ax_acc.cla()
        self.ax_prs.cla()
        self.ax_acc.patch.set_alpha(0)
        self.ax_acc.grid(True, lw=2, ls='--')

        self.ax_acc.set_title(f"state={data['state']:.0f}")
        acc_list = [
            data['acc_x'], data['acc_loc_x'], data['acc_peak_x'], data['acc_valley_x'],
            data['acc_y'], data['acc_loc_y'], data['acc_peak_y'], data['acc_valley_y'],
            data['acc_z'], data['acc_loc_z'], data['acc_peak_z'], data['acc_valley_z'],
            data['acc_energy'], data['acc_p2v_max_slp'],
        ]
        M = max(abs(t).max() for t in acc_list)
        colors = ['r', 'r', 'r', 'r', 'y', 'y', 'y', 'y', 'b', 'b', 'b', 'b', 'g', 'k']
        for i, y in enumerate(acc_list):
            if M < 20:
                self.ax_acc.set_ylim([-20, 20])
            if y < 0:
                y_min, y_max, v_align = y, 0, 'top'
                y_text = y_min
            else:
                y_min, y_max, v_align = 0, y, 'bottom'
                y_text = y_max
            self.ax_acc.vlines(i + 1, y_min, y_max, linewidth=20, colors=colors[i])
            self.ax_acc.text(i + 1, y_text, f'{y:.1f}', fontsize=12, horizontalalignment='center', verticalalignment=v_align)

        prs_list = [
            data['prs'] - data['prs_base'],
            data['prs_peak'] - data['prs_valley']
        ]
        colors = ['m', 'c']
        self.ax_prs.set_ylim([-0.5, 0.5])
        for i, y in enumerate(prs_list):
            j = i + len(acc_list) + 1
            if y < 0:
                y_min, y_max, v_align = y, 0, 'top'
                y_text = y_min
            else:
                y_min, y_max, v_align = 0, y, 'bottom'
                y_text = y_max
            self.ax_prs.vlines(j + 1, y_min, y_max, linewidth=20, colors=colors[i])
            self.ax_prs.text(j + 1, y_text, f'{y:.3f}', fontsize=12, horizontalalignment='center', verticalalignment=v_align)

        self.ax_acc.set_xticks(range(1, len(acc_list) + len(prs_list) + 1 + 1))
        self.ax_acc.set_xticklabels([
            'ax', 'alx', 'apx', 'avx',
            'ay', 'aly', 'apy', 'avy',
            'az', 'alz', 'apz', 'avz',
            'ae', 'ap2vslp', '',
            'pb', 'pp2v',
        ], fontsize=12, rotation=30, ha='center')

        self.draw()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.F = PlotDbgVars()
        self.twAlgRules.clicked.connect(self.on_tree_clicked)
        self.widget_root = None
        self.rules_bits = None  # 选中帧的rule bits位
        self.condition_tree = None

    def plot_debug_vars(self, data, frame):
        grid_layout = QGridLayout(self.gbDebugPlt)
        grid_layout.addWidget(self.F, 0, 1)
        self.F.plot_dbg_vars(data, frame)

    def show_algorithm_rules(self, c_tree: ConditionTree):
        self.twAlgRules.clear()
        self.twAlgRules.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.twAlgRules.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.twAlgRules.header().setStretchLastSection(False)
        self.twAlgRules.setColumnCount(1)
        self.twAlgRules.setHeaderLabels(['rule path'])
        self.widget_root = QTreeWidgetItem(self.twAlgRules)
        self.widget_root._tag = c_tree.tag
        self.widget_root._attrib = c_tree.attribute
        self.widget_root._text = c_tree.text
        self.widget_root.setText(0, c_tree.tag)

        def helper(_c_tree: ConditionTree, _widget_tree):
            if not _c_tree: return
            for child in _c_tree.children:
                w_child = QTreeWidgetItem(_widget_tree)
                w_child._tag = child.tag
                w_child._attrib = child.attribute
                w_child._text = child.text
                text = child.tag + (': ' + child.text if child.text else '')
                w_child.setText(0, text)
                helper(child, w_child)

        helper(c_tree, self.widget_root)
        self.condition_tree = c_tree
        self.twAlgRules.addTopLevelItem(self.widget_root)
        self.twAlgRules.expandAll()
        self.twAlgRules.show()

    def on_tree_clicked(self, QModelIndex):
        if self.rules_bits is None or self.widget_root is None:
            return

        father = son = self.twAlgRules.currentItem() or self.widget_root
        indicator = collections.defaultdict(str)
        path = []
        while father:
            if hasattr(father, '_attrib') and hasattr(father, '_text') and father._attrib:
                indicator[father._attrib['log_key']] = father._tag
            path.insert(0, father._tag)
            father = father.parent()
        path.pop()  # remove cur tag

        # todo: debug信息解析
        indicatorDict = ['root', 'cur_state', 'next_state', 'bit']

        my_red = QColor(255, 97, 0, 255)
        my_green = QColor(100, 160, 100, 255)

        def helper(cur: QTreeWidgetItem, this: MainWindow):
            path.append(cur._tag)
            if hasattr(cur, '_attrib') and cur._attrib and cur._attrib['log_key'] in indicatorDict:
                indicator[cur._attrib['log_key']] = cur._tag
                str_root = indicator['root']
                if cur._attrib['log_key'] == 'cur_state':
                    str_cur_state = indicator['cur_state']
                    cur_state = str(this.rules_bits[str_root + '_cur_state'].astype(int))
                    if str_cur_state == 'state_' + cur_state:
                        cur.setBackground(0, QBrush(Qt.green))
                    else:
                        cur.setBackground(0, QBrush(Qt.red))
                if cur._attrib['log_key'] == 'next_state':
                    str_cur_state = indicator['cur_state']
                    str_next_state = indicator['next_state']
                    cur_state = str(this.rules_bits[str_root + '_cur_state'].astype(int))
                    next_state = str(this.rules_bits[str_root + '_next_state'].astype(int))
                    if str_cur_state == 'state_' + cur_state and cur_state == next_state and str_next_state == 'state_freeze':
                        cur.setBackground(0, QBrush(Qt.green))
                        self.teAlgLog.setTextColor(my_green)
                    elif str_cur_state == 'state_' + cur_state and str_next_state == 'state_' + next_state:
                        cur.setBackground(0, QBrush(Qt.green))
                        self.teAlgLog.setTextColor(my_green)
                    elif 'state_end' in str_next_state:
                        if this.rules_bits.filter(regex='_end').astype(int).values == 0x0F:
                            cur.setBackground(0, QBrush(Qt.green))
                        else:
                            cur.setBackground(0, QBrush(Qt.red))
                    else:
                        cur.setBackground(0, QBrush(Qt.red))
                        self.teAlgLog.setTextColor(my_red)
                if cur._attrib['log_key'] == 'bit':
                    str_root = indicator['root']
                    str_cur_state = indicator['cur_state']
                    str_next_state = indicator['next_state']
                    str_bit = re.findall(r'(\d+)', indicator['bit'])[0]
                    show_str = ' -> '.join(path) + '\n' + cur._text
                    is_true = (this.rules_bits[str_root + '_' + str_cur_state + "_" + str_next_state].astype(int) >> int(str_bit)) & 1
                    if is_true:
                        cur.setBackground(0, QBrush(Qt.green))
                        self.teAlgLog.setTextColor(my_green)
                        self.teAlgLog.append(show_str)
                    else:
                        cur.setBackground(0, QBrush(Qt.red))
                        self.teAlgLog.setTextColor(my_red)
                        self.teAlgLog.append(show_str)
            for ci in range(cur.childCount()):
                helper(cur.child(ci), this)
            path.pop()

        self.teAlgLog.clear()
        self.teAlgLog.setTextColor(Qt.black)
        self.teAlgLog.append('============Start============')
        helper(son, self)
        self.teAlgLog.setTextColor(Qt.black)
        self.teAlgLog.append(f'state_{self.rules_bits["st_alg_rules_cur_state"]:.0f} -> state_{self.rules_bits["st_alg_rules_next_state"]:.0f}')
        self.teAlgLog.append('============End============\n')


if __name__ == '__main__':
    xml = XmlIO('config.xml', 'config.xml')
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show_algorithm_rules(xml.read())
    main.show()
    sys.exit(app.exec_())
