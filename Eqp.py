from PyQt5 import QtWidgets, QtGui, QtCore
import Eq
from scipy.optimize import fsolve
from math import *
import numpy as np
import pickle


class Equation(Eq.Ui_MainWindow):
    """Класс модуля Уравнений"""

    def __init__(self, widget):
        """Инициализация элементов модуля"""
        self.settings = [-100, 100, 0.5]
        self.widget = widget
        self.setupUi(self.widget)
        self.eqs = []
        self.selected = 0
        self.default_item = 'New Equation'
        self.Eadd.pressed.connect(lambda: self.add_eq())
        self.Eqlist.itemSelectionChanged.connect(lambda: self.select_item())
        self.Eqlist.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.Eqlist.addItem(QtWidgets.QListWidgetItem(self.default_item))
        self.Eq_edit.textChanged.connect(lambda: self.rewrite_selection())
        self.Edelete.pressed.connect(lambda: self.delete_item())
        self.Eqlist.setCurrentRow(0)
        self.Eq_edit.setSelection(0, 12)
        self.widget.resizeEvent = self.resize

        """Инициализация меню"""
        self.menu_help.triggered.connect(lambda: self.show_help())
        self.menu_file_new.triggered.connect(lambda: self.reset())
        self.menu_file_open.triggered.connect(lambda: self.load_eqs())
        self.menu_file_save.triggered.connect(lambda: self.save_eqs())
        self.menu_plot_save.triggered.connect(
            lambda: (
                self.build_plot(), self.widget.plot_widget.plot_save()))
        self.menu_plot_build.triggered.connect(
            lambda: (
                self.build_plot(), self.widget.plot_widget.show()))
        self.menu_plot_sett.triggered.connect(lambda: self.update_settings())

    def resize(self, *args, **kwargs):
        """Для масштабирования"""
        self.Eqlist.resize(self.widget.width() * 0.75,
                           self.widget.height() - 164)
        self.Eqroots.setGeometry(self.widget.width() * 0.75,
                                 170,
                                 self.widget.width() * 0.25,
                                 self.widget.height() - 164)
        self.Eq_edit.resize(self.widget.width(), self.Eq_edit.height())
        self.lb_roots.move(self.widget.width() * 0.875 - 100,
                           self.lb_roots.y())

    def reset(self):
        """Отчистка полей"""
        self.eqs = []
        self.Eqlist.clear()
        self.Eqroots.clear()
        self.Eqlist.addItem(QtWidgets.QListWidgetItem(self.default_item))
        self.Eq_edit.setText(self.default_item)
        self.Eqlist.setCurrentRow(0)
        self.Eq_edit.setSelection(0, 12)
        self.selected = 0

    def save_eqs(self):
        """Сохранение в файл"""
        try:
            name = QtWidgets.QFileDialog().getSaveFileName(self.widget,
                                                           'Save equations',
                                                           'unnamed.eqs',
                                                           'Equations (*.eqs)')
            if name[0]:
                with open(name[0], 'wb') as f:
                    pickle.dump(self.eqs, f)
        except Exception as exp:
            self.widget.show_exeption(exp)

    def show_help(self):
        """Вывод помощи"""
        mbox = QtWidgets.QMessageBox()
        mbox.setText('> Наберите Уравнение\n'
                     '> Нажмите добавить\n'
                     '> Постройте график\n')
        mbox.setWindowTitle('Как пользоваться')
        mbox.show()
        mbox.exec()

    def load_eqs(self):
        """Загрузка из файла"""
        try:
            self.reset()
            name = QtWidgets.QFileDialog().getOpenFileName(self.widget,
                                                           'Load equations',
                                                           '',
                                                           'Equations (*.eqs)')
            if name[0]:
                with open(name[0], 'rb') as f:
                    self.eqs = pickle.load(f)
                for eq in self.eqs:
                    self.Eqlist.addItem(QtWidgets.QListWidgetItem(eq))
                self.update_roots()
        except Exception as f:
            self.widget.show_exeption(f)

    def rewrite_selection(self):
        """Одновременное изменение текста в списке и поле"""
        try:  # TODO fix it
            self.Eqlist.selectedItems()[0].setText(self.Eq_edit.text())
        except Exception:
            pass

    def add_eq(self):
        """Добавление элемента в список."""
        try:
            new_eq = self.Eq_edit.text()
            if not self.selected and new_eq != self.default_item and\
                    new_eq not in self.eqs:
                self.eqs.append(new_eq)
                self.Eqlist.addItem(QtWidgets.QListWidgetItem(self.eqs[-1]))
                self.selected_to_default()
                self.update_roots()
        except Exception as f:
            self.widget.show_exeption(f)

    def selected_to_default(self):
        """Сброс выделения"""
        self.Eq_edit.setText(self.default_item)
        self.Eqlist.setCurrentRow(0)
        self.Eqlist.selectedItems()[0].setText(self.default_item)
        self.Eq_edit.setSelection(0, 12)

    def delete_item(self):
        """Удаление элемента"""
        if self.selected:
            a = self.selected - 1
            self.selected = 0
            self.eqs.pop(a)
            self.selected_to_default()
            self.Eqlist.takeItem(a + 1)
            self.update_roots()

    def select_item(self):
        """Выделение элемента

        Проверка, изменялся ли начальный элемент. если да -
        предупреждение, иначе - выделение выбранного элемента
        """
        if not self.selected and\
                self.Eqlist.item(0).text() != self.default_item:
            a = QtWidgets.QMessageBox()
            a.setWindowTitle('Внимание!')
            a.setText('Вы не сохранили измененное уравнение'
                      '. Вы уверены, что хотите отбросить изменения?')
            a.setStandardButtons(
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Discard)
            a.show()
            res = a.exec()
            if res == QtWidgets.QMessageBox.Ok:
                try:
                    self.Eqlist.item(0).setText(self.default_item)
                except:
                    return
            elif res == QtWidgets.QMessageBox.Discard:
                try:
                    self.selected_to_default()
                except:
                    pass
                return
        elif self.selected:
            new_eq = self.Eq_edit.text()
            self.eqs[self.selected - 1] = new_eq
        try:
            self.Eq_edit.setText(self.Eqlist.selectedItems()[0].text())
            self.selected = self.Eqlist.currentRow()
            self.update_roots()
        except Exception:
            pass

    def update_roots(self):
        """Нахождение печесечений"""
        self.Eqroots.clear()
        if self.eqs:
            func = eval('lambda x: ((' + ') - ('.join(self.eqs) + '))')
            a = fsolve(np.vectorize(func),
                       np.arange(*self.settings),
                       xtol=1e-5)
            for root in set(map(lambda x: x.round(2), a)):
                self.Eqroots.addItem(QtWidgets.QListWidgetItem(str(root)))

    def build_plot(self):
        """Построение общего графика функция"""
        self.widget.plot_widget.plot_clear()
        for eq in self.eqs:
            f = np.vectorize(eval('lambda x: ' + eq))
            ax = self.widget.plot_widget.plot(np.arange(*self.settings),
                                              f(np.arange(*self.settings)),
                                              label=eq)
            ax.legend(loc='upper left')

    def update_settings(self):
        """Настройки"""
        settbox = QtWidgets.QMessageBox()
        settbox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Discard)
        settbox.setWindowTitle('Настройки')
        settbox.setText('Минимально\tМаксимально\tШаг\t\t\n\n\n')
        r1, r2 = QtWidgets.QDoubleSpinBox(
            settbox), QtWidgets.QDoubleSpinBox(settbox)
        step = QtWidgets.QDoubleSpinBox(settbox)
        r2.setMinimum(-float('inf'))
        r2.setMaximum(float('inf'))
        step.setMinimum(-float('inf'))
        step.setMaximum(float('inf'))
        r1.setMinimum(-float('inf'))
        r1.setMaximum(float('inf'))
        dr1, dr2, dstep = self.settings
        r1.setValue(dr1)
        r2.setValue(dr2)
        step.setValue(dstep)
        r1.setSingleStep(0.01)
        r2.setSingleStep(0.01)
        step.setSingleStep(0.01)
        r1.move(30, 50)
        r2.move(150, 50)
        step.move(260, 50)
        settbox.show()
        ans = settbox.exec()
        if ans == QtWidgets.QMessageBox.Ok:
            r1v, r2v, stepv = r1.value(), r2.value(), step.value()
            self.settings = (min(r1v, r2v), max(r1v, r2v), stepv)
