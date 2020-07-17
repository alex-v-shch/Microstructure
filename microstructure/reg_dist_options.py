#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль редактирования параметров регулярного распределения
"""

from PyQt5 import QtWidgets


class EditRegularDistributionOptions(QtWidgets.QDialog):
    """Диалог редактирования параметров регулярного распределения."""

    def __init__(self, message, options, all_particles, regular_particles,
                 save_all_to_file, clean_distributions):
        super().__init__()

        self.message = message
        self.options = options
        self.all_particles = all_particles
        self.regular_particles = regular_particles
        self.save_all_to_file = save_all_to_file
        self.clean_distributions = clean_distributions

        self.resize(500, 300)

        self.setWindowTitle('Параметры регулярного распределения')

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setRowCount(3)

        if self.options['dim_ind'] == 1:
            self.table_widget.setColumnCount(3)
            self.table_widget.setHorizontalHeaderLabels(["x", "y", "z"])
        else:
            self.table_widget.setColumnCount(2)
            self.table_widget.setHorizontalHeaderLabels(["x", "y"])

        self.table_widget.setVerticalHeaderLabels(
            ["Начало отсчёта", "Приращение", "Количество"])
        self.table_widget.cellChanged.connect(self.changed)

        # заполнение массива
        for num, i in enumerate(self.options['regular_distribution']):
            self.table_widget.setItem(
                num, 0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.table_widget.setItem(
                num, 1, QtWidgets.QTableWidgetItem(str(i[1])))
            if self.options['dim_ind'] == 1:
                self.table_widget.setItem(
                    num, 2, QtWidgets.QTableWidgetItem(str(i[2])))

        def number_save():
            self.options['regular_distribution_diameter'] = self.radius.value()

        self.radius = QtWidgets.QDoubleSpinBox()
        self.radius.setRange(1, 100)
        self.radius.setValue(self.options['regular_distribution_diameter'])
        self.radius.setSingleStep(0.1)
        self.radius.setDecimals(1)
        self.radius.editingFinished.connect(number_save)

        self.form = QtWidgets.QFormLayout()
        self.form.addRow("&Диаметр", self.radius)

        self.button_save = QtWidgets.QPushButton("Сохранить в файл")
        self.button_save.clicked.connect(self.save_file)
        self.button_save.setDisabled(True)
        self.button_calc = QtWidgets.QPushButton("Расчёт")
        self.button_calc.clicked.connect(self.calc_regular_distribution)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table_widget)
        self.layout.addLayout(self.form)
        self.layout.addWidget(self.button_calc)
        self.layout.addWidget(self.button_save)

        self.setLayout(self.layout)

        self.show()

    def calc_regular_distribution(self):
        """Calculation regular distribution."""

        import shapes

        self.regular_particles = []  # очистка

        x0 = self.options['regular_distribution'][0][0]
        dx = self.options['regular_distribution'][1][0]
        nx = self.options['regular_distribution'][2][0]

        y0 = self.options['regular_distribution'][0][1]
        dy = self.options['regular_distribution'][1][1]
        ny = self.options['regular_distribution'][2][1]

        if self.options['dim_ind'] == 1:  # 3D
            z0 = self.options['regular_distribution'][0][2]
            dz = self.options['regular_distribution'][1][2]
            nz = self.options['regular_distribution'][2][2]

        for x in [x0 + dx * i for i in range(nx)]:
            for y in [y0 + dy * i for i in range(ny)]:
                if self.options['dim_ind'] == 1:  # 3D
                    for z in [z0 + dz * i for i in range(nz)]:
                        particle = shapes.Sphere(
                            x, y, z,
                            self.options['regular_distribution_diameter'])
                        self.regular_particles.append(particle)
                else:  # 2D
                    # z = 0
                    particle = shapes.Circle(
                        x, y, self.options['regular_distribution_diameter'])
                    self.regular_particles.append(particle)

        self.all_particles.extend(
            self.regular_particles)  # расширить список всех частиц

        self.button_save.setEnabled(True)
        self.clean_distributions.setEnabled(True)

        self.message('Регулярное распределение частиц посчитано')

    def save_file(self):

        self.save_all_to_file(self.regular_particles)
        self.close()

    def changed(self):

        for current_qtable_widget_item in self.table_widget.selectedItems():
            self.options[
                'regular_distribution'][current_qtable_widget_item.row()][
                    current_qtable_widget_item.column()] = int(
                        current_qtable_widget_item.text())
