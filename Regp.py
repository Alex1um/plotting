from PyQt5 import QtWidgets, QtCore, QtGui
import Reg
import pandas
import sqlite3
from types import FunctionType
from scipy.optimize import minimize, OptimizeResult
import numpy as np


class Regression(Reg.Ui_MainWindow):
    templates = {
        (lambda x, k, b, *args: k * x + b,
         lambda *args: '{}*x + {}'.format(*args)),
        (lambda x, w0, w1, w2, *args: w0 * x ** 2 + w1 * x + w2,
         lambda *args: '{}*x**2 + {}*x + {}'.format(*args)),
        (lambda x, w0, w1, w2, *args: w0 / (x + w1) + w2,
         lambda *args: '{} / (x + {}) + {}'.format(*args))
    }

    def __init__(self, widget):
        self.widget = widget
        self.setupUi(self.widget)
        self.data = []
        self.selected = []
        self.bt_clear_selection.pressed.connect(
            lambda: self.main_table.clearSelection())
        self.main_table.itemSelectionChanged.connect(lambda: self.update_reg())
        self.bt_eq_run.pressed.connect(lambda: self.find_equation())
        self.bt_all_selection.pressed.connect(
            lambda: self.main_table.selectAll())
        self.bt_eq_reset.pressed.connect(
            lambda: self.prev_eqs.clear())

        self.menu_file_new.triggered.connect(lambda: self.reset())
        self.menu_plot_sett.triggered.connect(lambda: self.find_equation())
        self.menu_plot_build.triggered.connect(
            lambda: (
                self.built_plot(), self.widget.plot_widget.show()))
        self.menu_plot_save.triggered.connect(
            lambda: (
                self.built_plot(), self.widget.plot_widget.plot_save()))
        self.menu_file_open.triggered.connect(lambda: self.load_table())

    def load_table(self):
        name, _ = QtWidgets.QFileDialog().getOpenFileName(self.widget,
                                                          'Load table',
                                                          '',
                                                          'Table (*.csv '
                                                          '*.xls,'
                                                          ' *.xlsx, '
                                                          '*.db '
                                                          '*.json)')
        ext = name[name.rfind('.') + 1:]
        if ext == 'csv':
            self.data = pandas.read_csv(name)
        elif ext == 'json':
            self.data = pandas.read_json(name)
        elif ext in {'xls', 'xlsx'}:
            self.data = pandas.read_excel(name)
        elif ext == '.db':
            db_connection = sqlite3.connect(name)
            self.data = pandas.read_sql(name, db_connection)

        # self.main_table.setSelectionMode(
        #     QtWidgets.QAbstractItemView.MultiSelection)
        col_len = self.data.keys().__len__()
        row_len = self.data.__len__()
        self.main_table.setRowCount(row_len)
        self.main_table.setColumnCount(col_len)
        self.main_table.setHorizontalHeaderLabels(self.data.keys())
        for i, row in self.data.iterrows():
            for j in range(col_len):
                self.main_table.setItem(
                    i,
                    j,
                    QtWidgets.QTableWidgetItem(str(row[j])))

    def update_reg(self):
        # item: QtWidgets.QTableWidgetItem = None
        selected = dict()
        for item in self.main_table.selectedItems():
            coll = item.column()
            if coll in selected:
                selected[coll].append(item.text())
            else:
                selected[coll] = [item.text()]
        selected = list(selected.items())

        if selected:
            newselected = max(selected, key=lambda x: len(x[1]))
            selected.remove(newselected)
            try:
                self.selected = list([float(i)] for i in newselected[1])
                for item in selected:
                    for i in range(len(item[1])):
                        try:
                            self.selected[i].append(float(item[1][i]))
                        except IndexError as f:
                            self.widget.show_exeption(f)
                self.selected.sort(key=lambda x: x[0])
            except ValueError:
                self.widget.show_exeption('Values must be float or integer')

    def reset(self):
        self.selected = []
        self.data = []
        self.main_table.clear()
        self.prev_eqs.clear()

    def built_plot(self):
        self.widget.plot_widget.plot_clear()
        # self.widget.plot_widget.plot_clear()
        for item in self.selected:
            self.widget.plot_widget.plot(*item, mode='scatter')
        datax = tuple(map(lambda x: x[0], self.selected))
        for i in range(len(self.templates)):
            eq = self.prev_eqs.item(i).text()
            f = eval('lambda x:' + eq)
            datay = tuple(map(lambda x: f(x), datax))
            ax = self.widget.plot_widget.plot(datax, datay, label=eq)
            ax.legend(loc='upper left')

    def find_equation(self):

        def error(args, template: FunctionType):
            er = 0
            for elem in self.selected:
                er += (template(elem[0], *args) - elem[1]) ** 2
            return er

        self.prev_eqs.clear()
        for template in self.templates:
            res = minimize(
                error,
                np.ones(5),
                template[0],
                method='Nelder-Mead')
            self.prev_eqs.addItem(
                QtWidgets.QListWidgetItem(
                    template[1](*map(lambda x: round(x, 2), res['x']))))
            # datax = tuple(map(lambda x: x[0], self.selected))
            # datay = tuple(map(lambda x: template(x, *res['x']), datax))
            # self.widget.plot_widget.plot(datax, datay)
