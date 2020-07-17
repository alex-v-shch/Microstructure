#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Программа рассчитывает заполнение микрообъёма частицами
"""

import csv
import os
import sys
import webbrowser
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import uic, Qt, QtCore, QtWidgets, QtGui
from builtins import float


class Application(QtWidgets.QMainWindow):
    """Программа с графическим интерфейсом."""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        uic.loadUi('MainWindow.ui', self)

        self.program = 'Microstructure'
        self.copyright = '© Alexander Shchemelinin <alexshch82@gmail.com>, 2020'
        self.help = 'F1: Help'

        self.options = {
            'dim_tup': ('2D', '3D'),
            'dim_ind': 1,
            'var_tup': ('целиком', 'частично'),
            'var_ind': 1,
            'def_tup': ('количество частиц', 'степень заполнения'),
            'def_ind': 1,
            'matrix': 100.,
            'gap': 1.,
            'boundary_repulsion': 20,
            'max_iter': 1000,
            'fractions_definition': [[50., 0.5], ],
            'regular_distribution': [[0, 0, 0], [30, 30, 30], [3, 3, 3]],
            'regular_distribution_diameter': 20.
        }

        self.working_directory()

        self.fractions_filling_degree = {}  # степень заполнения по фракциям

        # признак активизации расчёта распределения частиц
        self.process_running = False

        self.all_particles = []  # все имеющиеся распределения частиц
        self.random_particles = []  # случайное распределение частиц
        # загруженные файлы (формат строки файла частиц: x, y, z, diameter)
        self.loaded_files = []
        self.loaded_particles = []  # загруженные из файла частицы
        self.regular_particles = []  # частицы с регулярным распределением

        super().setWindowTitle(self.program)

        self.setWindowIcon(QtGui.QIcon(os.path.join('images', 'starred.png')))

        self.statusbar.addWidget(QtWidgets.QLabel(self.help), stretch=1)
        self.statusbar.addPermanentWidget(
            QtWidgets.QLabel(self.copyright), stretch=0)

        self.current_event_label = QtWidgets.QLabel()
        self.statusbar.addWidget(self.current_event_label)

        # выравнивание окна приблизительно по центру экрана
        desktop = QtWidgets.QApplication.desktop()
        x = (desktop.width() - self.width()) // 2
        y = (desktop.height() - self.height()) // 2
        self.move(x, y)

        # панели инструментов (набор иконок Adwaita/32x32)
        self.toolbar1 = self.addToolBar('Панель инструментов')

        self.exit_action = QtWidgets.QAction(
            QtGui.QIcon(os.path.join('images', 'application-exit.png')),
            'Выход', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Выход из программы')
        self.exit_action.triggered.connect(QtWidgets.qApp.quit)
        self.toolbar1.addAction(self.exit_action)

        self.toolbar1.addSeparator()

        self.workDir.setIcon(
            QtGui.QIcon(os.path.join('images', 'folder-open.png')))
        self.workDir.setStatusTip('Задать рабочий каталог')
        self.toolbar1.addAction(self.workDir)

        self.editOptions.setIcon(
            QtGui.QIcon(os.path.join('images', 'preferences-desktop.png')))
        self.editOptions.setStatusTip('Задать параметры расчёта')
        self.toolbar1.addAction(self.editOptions)

        self.editFractions.setIcon(
            QtGui.QIcon(os.path.join('images',
                                     'preferences-desktop-personal.png')))
        self.editFractions.setStatusTip('Задать параметры фракций')
        self.toolbar1.addAction(self.editFractions)

        self.toolbar1.addSeparator()

        self.loadFile.setIcon(
            QtGui.QIcon(os.path.join('images', 'insert-object.png')))
        self.loadFile.setStatusTip(
            'Загрузить (с добавлением) распределение частиц из файла')
        self.toolbar1.addAction(self.loadFile)

        self.toolbar1.addSeparator()

        self.generator.setIcon(
            QtGui.QIcon(os.path.join('images', 'view-sort-descending.png')))
        self.generator.setStatusTip(
            'Сгенерировать регулярное распределение частиц')
        self.toolbar1.addAction(self.generator)

        self.toolbar1.addSeparator()

        self.cleanDistributions.setIcon(
            QtGui.QIcon(os.path.join('images', 'edit-delete.png')))
        self.cleanDistributions.setStatusTip(
            'Очистить распределение частиц из файла')
        self.toolbar1.addAction(self.cleanDistributions)

        self.processStart.setIcon(
            QtGui.QIcon(os.path.join('images', 'media-playback-start.png')))
        self.processStart.setStatusTip('Расчёт распределения частиц')
        self.toolbar1.addAction(self.processStart)

        self.processStop.setIcon(
            QtGui.QIcon(os.path.join('images', 'process-stop.png')))
        self.processStop.setStatusTip('Остановить расчёт распределения частиц')
        self.toolbar1.addAction(self.processStop)

        self.toolbar1.addSeparator()

        self.visualisation.setIcon(
            QtGui.QIcon(os.path.join('images', 'emblem-photos.png')))
        self.visualisation.setStatusTip('Визуализация результатов расчёта')
        self.toolbar1.addAction(self.visualisation)

        self.saveAll.setIcon(
            QtGui.QIcon(os.path.join('images', 'document-save.png')))
        self.saveAll.setStatusTip('Сохранить распределение частиц в файл')
        self.toolbar1.addAction(self.saveAll)

        self.filling.setIcon(
            QtGui.QIcon(os.path.join('images', 'battery-good.png')))
        self.filling.setStatusTip(
            'Расчитать общую степень заполнения матрицы частицами')
        self.toolbar1.addAction(self.filling)

        # обработчики действий
        self.workDir.triggered.connect(self.set_work_dir)
        self.editOptions.triggered.connect(self.edit_options)
        self.editFractions.triggered.connect(self.edit_fractions)

        self.loadFile.triggered.connect(self.load_from_file)
        self.generator.triggered.connect(self.regular_distribution)

        self.cleanDistributions.triggered.connect(self.clean_distributions)
        self.processStart.triggered.connect(self.process_start)
        self.processStop.triggered.connect(self.process_stop)
        self.visualisation.triggered.connect(
            lambda: self.plot(self.all_particles))
        self.saveAll.triggered.connect(
            lambda: self.save_all_to_file(self.all_particles))
        self.filling.triggered.connect(self.filling_degree)

        self.disable_menus()

    def keyPressEvent(self, event):
        """Запуск файла помощи в браузере по-умолчанию."""

        if event.key() == QtCore.Qt.Key_F1:
            webbrowser.open(os.path.abspath('README.html'))

    def working_directory(self):
        """Рабочий каталог."""

        app_dir = os.path.dirname(os.path.abspath(__file__))

        if 'work_dir.txt' in os.listdir(app_dir):
            with open(os.path.join(app_dir, 'work_dir.txt'), 'r') as f:
                path = f.readline()
                if os.path.exists(path):
                    self.work_dir = path
                else:
                    self.work_dir = os.path.join(app_dir, 'demo')

        else:
            self.work_dir = os.path.join(app_dir, 'demo')

        self.message('Рабочий каталог: ' + self.work_dir)

    def set_work_dir(self):
        """Выбрать рабочий каталог."""

        self.work_dir = os.path.normpath(
            QtWidgets.QFileDialog.getExistingDirectory(
                parent=None, caption="Рабочий каталог",
                directory=self.work_dir))
        if self.work_dir:
            with open(os.path.join(os.path.dirname(__file__),
                                   'work_dir.txt'), 'w') as f:
                f.write(self.work_dir)

            self.textEdit.clear()  # очистить консоль

            self.message('Выбран рабочий каталог: ' + self.work_dir)

            self.disable_menus()

    def disable_menus(self):
        """Настройка изначальной доступности пунктов меню."""

        self.cleanDistributions.setDisabled(True)
        self.processStop.setDisabled(True)
        self.saveAll.setDisabled(True)

    def process_stop(self):
        self.process_running = False
        self.processStart.setEnabled(True)
        self.processStop.setDisabled(True)

    def message(self, message):
        """Вывод сообщений в графическую консоль."""

        zap_gui = '$ '
        self.textEdit.append(zap_gui + message)

    def edit_options(self):
        import options
        self.dialog1 = options.EditOptions(self.message, self.options)

    def edit_fractions(self):
        import fractions
        self.dialog2 = fractions.EditFractions(self.message, self.options)

    def regular_distribution(self):
        """Расчёт параметров регулярного распределения."""

        import reg_dist_options
        self.dialog3 = reg_dist_options.EditRegularDistributionOptions(
            self.message, self.options, self.all_particles,
            self.regular_particles, self.save_all_to_file,
            self.cleanDistributions)

    def process_start(self):
        """Расчёт распределения частиц"""

        import random_creation

        if self.options['def_ind'] == 0:  # кол-во частиц
            random_creation.preset_particles_number(self)
        elif self.options['def_ind'] == 1:  # степень заполнения
            random_creation.preset_filling_degree(self)

    def filling_degree(self):
        """Расчёт степени заполнения."""

        import shapes
        import fill_deg

        space = {}  # площадь либо объём

        if self.options['dim_ind'] == 0:  # 2D
            matrix = shapes.SquareMatrix(self.options['matrix'])
        elif self.options['dim_ind'] == 1:  # 3D
            matrix = shapes.CubeMatrix(self.options['matrix'])

        for particle in self.all_particles:
            if particle.d in space:
                space[particle.d] += fill_deg.space(matrix, particle)
            else:
                space[particle.d] = fill_deg.space(matrix, particle)

        for diameter in sorted(space):
            self.fractions_filling_degree[diameter] = fill_deg.filling(
                matrix, space[diameter])

        for diameter in sorted(self.fractions_filling_degree):
            self.message(
                'KV = {0:.3f}, диаметр частиц = {1:.1f}'.format(
                    self.fractions_filling_degree[diameter], diameter))

        self.message(
            '<font color="brown"><b>KV = {0:.3f}, по всем фракциям<b></font>'.
            format(sum(self.fractions_filling_degree.values())))

    def plot(self, data):
        """Визуализация матрицы с частицами."""

        plt.close('all')
        plt.figure(num='Микроструктура {0}'.format(
            self.options['dim_tup'][self.options['dim_ind']]),\
                figsize=(7, 7), dpi=100)

        if self.fractions_filling_degree:
            title = ''
            for diameter in self.fractions_filling_degree:
                title += 'd={0:.1f}, KV={1:.3f}; '.format(
                    diameter, self.fractions_filling_degree[diameter])
            title += 'ALL={0:.3f}'.format(
                sum(self.fractions_filling_degree.values()))
            plt.title(title)

        ax = plt.axes()

        plt.xlim(0, self.options['matrix'])
        plt.ylim(0, self.options['matrix'])

        data_list = []
        for i in data:
            if 'z' in i.__dict__:  # 3D
                data_list.append((i.x, i.y, i.z, i.d))
            else:  # 2D
                data_list.append((i.x, i.y, 0., i.d))

        array = np.array(
            data_list, dtype=[('x', np.float64), ('y', np.float64),
                              ('z', np.float64), ('d', np.float64)])
        array.sort(order='z')  # сортировка по оси "z"

        for x, y, _, d in array:
            cir = patches.Circle(
                (x, y), radius=d/2, fill=True,
                edgecolor='black', facecolor='gray', alpha=0.7)
            ax.add_patch(cir)

        plt.xlabel('X')
        plt.ylabel('Y')

        plt.show()

    def clean_distributions(self):
        """Очистить все распределения."""

        self.loaded_files = []
        self.loaded_particles = []
        self.regular_particles = []
        self.random_particles = []
        self.all_particles = []
        self.fractions_filling_degree = {}

        self.message('Распределение частиц очищено')
        self.cleanDistributions.setDisabled(True)

    def load_from_file(self):
        """Загрузить распределение из файла."""

        try:
            loaded_file, _ = QtWidgets.QFileDialog.getOpenFileName(
                None, 'Введите имя файла', self.work_dir,
                'Файлы распределений частиц (*.tsv)')

            self.loaded_files.append(loaded_file)

            import shapes

            with open(loaded_file, 'r') as f:
                loaded = []
                for strings_list in csv.reader(f, delimiter='\t'):
                    numbers_list = []
                    for string in strings_list:
                        numbers_list.append(float(string))
                    loaded.append(tuple(numbers_list))

                # определение размерности задачи
                for i in loaded:
                    if i[2]:  # хотя бы один параметр z != 0
                        self.options['dim_ind'] = 1
                        break

                for i in loaded:
                    if self.options['dim_ind'] == 0:  # 2D
                        self.loaded_particles.append(
                            shapes.Circle(x=i[0], y=i[1], d=i[3]))
                    elif self.options['dim_ind'] == 1:  # 3D
                        self.loaded_particles.append(
                            shapes.Sphere(x=i[0], y=i[1], z=i[2], d=i[3]))

                self.message('Загружен файл: {0}'.format(loaded_file))

            self.all_particles.extend(self.loaded_particles)

            self.cleanDistributions.setEnabled(True)

        except FileNotFoundError:
            self.message(
                'Распределение не загружено!\nПричина: не введено имя файла')

    def save_all_to_file(self, data):
        """Сохранить распределение в файл."""

        data_list = []
        for i in data:
            if 'z' in i.__dict__:  # 3D
                data_list.append((i.x, i.y, i.z, i.d))
            else:  # 2D
                data_list.append((i.x, i.y, 0., i.d))

        array = np.array(data_list)

        try:
            file_name = os.path.join(
                self.work_dir,
                '{0}.tsv'.format(
                    self.options['dim_tup'][self.options['dim_ind']]))
            file, _ = QtWidgets.QFileDialog.getSaveFileName(
                None, 'Введите имя файла', file_name,
                'Файлы распределений частиц (*.tsv)')

            np.savetxt(file, array, delimiter='\t')
            self.message('Сохранён файл: {0}'.format(file))

        except FileNotFoundError:
            self.message(
                'Распределение не сохранено!\nПричина: не введено имя файла')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    splash = QtWidgets.QSplashScreen(
        QtGui.QPixmap(os.path.join('images', 'cat.png')),
        Qt.Qt.WindowStaysOnTopHint)
    splash.showMessage(
        'Программа рассчитывает заполнение микрообъёма частицами',
        Qt.Qt.AlignHCenter | Qt.Qt.AlignBottom, Qt.Qt.black)
    splash.show()

    myapp = Application()
    myapp.show()

    sys.exit(app.exec_())
