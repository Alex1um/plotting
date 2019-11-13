from PyQt5 import QtWidgets, QtCore, QtGui
import Reg
import pandas
import sqlite3
from types import FunctionType
from scipy.optimize import minimize, OptimizeResult
import numpy as np


class Regression(Reg.Ui_MainWindow):
    """
    Клас регрессиии
    """
    templates = {
        (lambda x, k, b, *args: k * x + b,
         lambda *args: '{}*x + {}'.format(*args)),
        (lambda x, w0, w1, w2, *args: w0 * x ** 2 + w1 * x + w2,
         lambda *args: '{}*x**2 + {}*x + {}'.format(*args)),
        (lambda x, w0, w1, w2, *args: w0 / (x + w1) + w2,
         lambda *args: '{} / (x + {}) + {}'.format(*args))
    }

    def __init__(self, widget):
        """Инициализация"""
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
        self.widget.resizeEvent = self.resize

        """Инициализация меню"""
        self.menu_help.triggered.connect(lambda: self.show_help())
        self.menu_file_save.triggered.connect(lambda: self.save_table())
        self.menu_file_new.triggered.connect(lambda: self.reset())
        self.menu_plot_sett.triggered.connect(lambda: self.find_equation())
        self.menu_plot_build.triggered.connect(
            lambda: (
                self.built_plot(), self.widget.plot_widget.show()))
        self.menu_plot_save.triggered.connect(
            lambda: (
                self.built_plot(), self.widget.plot_widget.plot_save()))
        self.menu_file_open.triggered.connect(lambda: self.load_table())

    def resize(self, *args, **kwargs):
        """для масштабирования"""
        self.main_table.resize(self.widget.width() * 0.7,
                               self.widget.height() - 111)
        self.prev_eqs.setGeometry(self.widget.width() * 0.7,
                                  60,
                                  self.widget.width() * 0.3,
                                  self.widget.height() - 111)
        self.bt_clear_selection.resize(self.widget.width() * 0.35,
                                       self.bt_clear_selection.height())
        self.bt_all_selection.setGeometry(self.widget.width() * 0.35,
                                          self.bt_all_selection.y(),
                                          self.widget.width() * 0.35,
                                          self.bt_all_selection.height())
        self.bt_eq_reset.setGeometry(self.widget.width() * 0.695,
                                     self.bt_eq_reset.y(),
                                     self.widget.width() * 0.127,
                                     self.bt_eq_reset.height())
        self.bt_eq_run.setGeometry(self.widget.width() * 0.82,
                                   self.bt_eq_run.y(),
                                   self.widget.width() * 0.187,
                                   self.bt_eq_run.height())

    def show_help(self):
        """Вывод помощи"""
        mbox = QtWidgets.QMessageBox()
        mbox.setText('> Откройте таблицу.\n'
                     '> Выделите 2 стлбца одинакового размера\n'
                     '> Нажмите "вычислить" для вычисления уравнений\n'
                     '> Постройте график')
        mbox.setWindowTitle('Как пользоваться')
        mbox.show()
        mbox.exec()

    def save_table(self):
        """Сохранение выделенного"""
        name = QtWidgets.QFileDialog().getSaveFileName(self.widget,
                                                       'Save Selected',
                                                       'unnamed.csv',
                                                       'Table (*.csv'
                                                       ' *.db'
                                                       ' *.xls '
                                                       '*.xlsx)')[0]
        if name:
            data = dict()
            selected = self.group_selected()
            labels = tuple(self.data.keys())
            for i, k in selected.items():
                data[labels[i]] = k
            data = pandas.DataFrame.from_dict(data)
            ext = name[name.rfind('.') + 1::]
            if ext == 'csv':
                data.to_csv(name)
            elif ext == 'db':
                db_connection = sqlite3.connect(name)
                name = 'Unnamed'

                tables = db_connection.execute(
                    'select name from sqlite_master'
                    ' where type = "table"').fetchall()
                tables = tuple(*zip(*tables))
                new_table = QtWidgets.QMessageBox(self.widget)
                new_table.setStandardButtons(QtWidgets.QMessageBox.Ok |
                                             QtWidgets.QMessageBox.Discard)

                new_table_name = QtWidgets.QLineEdit(new_table)
                new_table_name.setText(name)
                new_table_name.move(150, 40)
                new_table.setText(
                    'Указанная таблица уже существует, заменить?\n\n' +
                    '\t' * 6 if new_table_name.text() in tables else
                    'Укажите имя таблицы\n\n' + '\t' * 6)
                new_table_name.textChanged.connect(
                    lambda: new_table.setText(
                        'Указанная таблица уже существует, заменить?\n\n' +
                        '\t' * 6 if new_table_name.text() in tables else
                        'Укажите имя таблицы\n\n' + '\t' * 6))
                new_table.resize(200, 100)
                new_table.show()
                ret = new_table.exec()
                if ret == QtWidgets.QMessageBox.Ok:
                    name = new_table_name.text()
                    data.to_sql(name, db_connection)
            elif ext in {'xls', 'xlsx'}:
                data.to_excel(name)

    def load_table(self):
        """Загрузка таблицы"""
        name, _ = QtWidgets.QFileDialog().getOpenFileName(self.widget,
                                                          'Load table',
                                                          '',
                                                          'Table (*.csv '
                                                          '*.xls '
                                                          ' *.xlsx '
                                                          '*.db '
                                                          '*.json)')
        if name:
            ext = name[name.rfind('.') + 1:]
            if ext == 'csv':
                self.data = pandas.read_csv(name)
            elif ext == 'json':
                self.data = pandas.read_json(name)
            elif ext in {'xls', 'xlsx'}:
                self.data = pandas.read_excel(name)
            elif ext in {'db', 'sqlite'}:
                db_connection = sqlite3.connect(name)

                tables = db_connection.execute(
                    'select name from sqlite_master'
                    ' where type = "table"').fetchall()
                if len(tables) > 1:
                    msg_box = QtWidgets.QMessageBox()
                    msg_box.setText('Выберите нужную таблицу:\t\t\t')
                    cb = QtWidgets.QComboBox(msg_box)
                    cb.addItems(*zip(*tables))
                    cb.move(230, 10)
                    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok |
                                               QtWidgets.QMessageBox.Discard)
                    msg_box.setWindowTitle('Выберите нужную таблицу')
                    msg_box.show()
                    if msg_box.exec() == msg_box.Ok:
                        name = cb.currentText()
                    else:
                        return
                else:
                    name = tables[0][0]
                self.data = pandas.read_sql_query(f'SELECT * FROM "{name}"',
                                                  db_connection)
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

    def group_selected(self):
        """Группировка выделенного"""
        selected = dict()
        for item in self.main_table.selectedItems():
            coll = item.column()
            if coll in selected:
                selected[coll].append(item.text())
            else:
                selected[coll] = [item.text()]
        return selected

    def update_reg(self):
        """Обработка выделенных данных"""
        # item: QtWidgets.QTableWidgetItem = None

        selected = list(self.group_selected().items())

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
        """Сброс"""
        self.selected = []
        self.data = []
        self.main_table.clear()
        self.prev_eqs.clear()

    def built_plot(self):
        """Прорисовка графов"""
        self.widget.plot_widget.plot_clear()
        # self.widget.plot_widget.plot_clear()
        for item in self.selected:
            self.widget.plot_widget.plot(*item, mode='scatter')
        datax = tuple(map(lambda x: x[0], self.selected))
        for i in range(len(self.templates)):
            try:
                eq = self.prev_eqs.item(i).text()
                f = eval('lambda x:' + eq)
                datay = tuple(map(lambda x: f(x), datax))
                ax = self.widget.plot_widget.plot(datax, datay, label=eq)
                ax.legend(loc='upper left')
            except Exception:
                pass

    def find_equation(self):
        """
        Нахождение уравнения по точкам
        :return:
        """
        def error(args, template: FunctionType):
            """

            :param args: Переменные
            :param template: Шаблон уравнения
            :return: Ошибка
            """
            er = []
            for elem in self.selected:
                er.append(abs(template(elem[0], *args) - elem[1]))
                print(abs(template(elem[0], *args) - elem[1]))
            return max(er)

        self.prev_eqs.clear()
        for template in self.templates:
            res = minimize(
                error,
                np.ones(5),
                template[0],
                method='Nelder-Mead')
            self.prev_eqs.addItem(
                QtWidgets.QListWidgetItem(
                    template[1](*map(lambda x: round(x, 3), res['x']))))
            # datax = tuple(map(lambda x: x[0], self.selected))
            # datay = tuple(map(lambda x: template(x, *res['x']), datax))
            # self.widget.plot_widget.plot(datax, datay)
