from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from modules import Eqp, Regp
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, \
    NavigationToolbar2QT
import matplotlib.figure as figure
import numpy as np


class Plotting(QtWidgets.QMainWindow):
    """Основной Виджет"""
    def __init__(self):
        super().__init__()
        self.plot_widget = PlotWidget()
        # self.change_interface('Equations')
        self.current_ui = Eqp.Equation(self)
        self.current_ui.menu_type_reg.triggered.connect(
            lambda: self.change_interface('Regression'))
        self.show()

    def change_interface(self, mode):
        """Смена модуля"""
        if mode == 'Equations':
            self.current_ui.reset()
            self.current_ui = Eqp.Equation(self)
            self.current_ui.menu_type_reg.triggered.connect(
                lambda: self.change_interface('Regression'))
        elif mode == 'Regression':
            self.current_ui.reset()
            self.current_ui = Regp.Regression(self)
            self.current_ui.menu_type_eq.triggered.connect(
                lambda: self.change_interface('Equations'))

    def show_exeption(self, message, title='Error'):
        """выброс ошибки(или текста)"""
        e_msg_box = QtWidgets.QMessageBox(self)
        e_msg_box.setWindowTitle(title)
        e_msg_box.setText(repr(message))
        e_msg_box.show()
        e_msg_box.exec()


class PlotWidget(QtWidgets.QWidget):
    """Виджет для рисования графиков"""
    def __init__(self):
        super().__init__()
        self.canvas = FigureCanvas(self)
        self.panel = NavigationToolbar2QT(self.canvas, self, (0, 0))

    def plot(self, *data, mode='plot', **kwargs):
        """Рисование графов"""
        ax = self.canvas.figure.add_subplot(111)
        if mode == 'plot':
            ax.plot(*data, **kwargs)
        elif mode == 'scatter':
            ax.scatter(*data, **kwargs)
        return ax

    def plot_clear(self):
        """Отчистка графика"""
        self.canvas.figure.clear()

    def plot_save(self):
        """Сохранение графика"""
        name = QtWidgets.QFileDialog().getSaveFileName(self,
                                                       'New File',
                                                       'unnamed.png',
                                                       'Images (*.png)')
        if name[0]:
            self.canvas.figure.savefig(name[0])


class FigureCanvas(FigureCanvasQTAgg):
    """Виджет графика"""
    def __init__(self, parent=None, width=7, height=7, dpi=100):
        self.fig = figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)


app = QtWidgets.QApplication(sys.argv)
# p = PlotWidget()
# p.plot(np.arange(1000), np.vectorize(lambda x: x**3)(range(1000)))
# p.plot(np.arange(1000), np.vectorize(lambda x: x**2)(range(1000)))
# p.show()
a = Plotting()
app.exec()
