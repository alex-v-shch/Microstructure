#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль редактирования параметров
"""

from PyQt5 import QtWidgets


class EditOptions(QtWidgets.QDialog):
    """Диалог редактирования параметров."""

    def __init__(self, message, options):
        super().__init__()
        self.message = message
        self.options = options

        self.max_matrix = 1000.
        self.max_gap = 100.
        self.max_boundary_repulsion = 100
        self.max_iter = 1000000

        self.init_ui()

    def init_ui(self):
        def dim_save(index):
            dimension.setCurrentIndex(index)
            self.options['dim_ind'] = index

        def var_save(index):
            variant.setCurrentIndex(index)
            self.options['var_ind'] = index

        def def_save(index):
            definition.setCurrentIndex(index)
            self.options['def_ind'] = index

        dimension = QtWidgets.QComboBox()
        dimension.addItem(self.options['dim_tup'][0])
        dimension.addItem(self.options['dim_tup'][1])
        dimension.setCurrentIndex(self.options['dim_ind'])
        dimension.currentIndexChanged.connect(dim_save)

        variant = QtWidgets.QComboBox()
        variant.addItem(self.options['var_tup'][0])
        variant.addItem(self.options['var_tup'][1])
        variant.setCurrentIndex(self.options['var_ind'])
        variant.currentIndexChanged.connect(var_save)

        definition = QtWidgets.QComboBox()
        definition.addItem(self.options['def_tup'][0])
        definition.addItem(self.options['def_tup'][1])
        definition.setCurrentIndex(self.options['def_ind'])
        definition.currentIndexChanged.connect(def_save)

        def number_save():
            self.options['matrix'] = matrix.value()
            self.options['gap'] = gap.value()
            self.options['boundary_repulsion'] = boundary_repulsion.value()
            self.options['max_iter'] = max_iter.value()

        matrix = QtWidgets.QDoubleSpinBox()
        matrix.setRange(0.1, self.max_matrix)
        matrix.setValue(self.options['matrix'])
        matrix.setSingleStep(0.1)
        matrix.setDecimals(1)
        matrix.editingFinished.connect(number_save)

        gap = QtWidgets.QDoubleSpinBox()
        gap.setRange(0.1, self.max_gap)
        gap.setValue(self.options['gap'])
        gap.setSingleStep(0.1)
        gap.setDecimals(1)
        gap.editingFinished.connect(number_save)

        boundary_repulsion = QtWidgets.QSpinBox()
        boundary_repulsion.setSingleStep(1)
        boundary_repulsion.setRange(1, self.max_boundary_repulsion)
        boundary_repulsion.setValue(self.options['boundary_repulsion'])
        boundary_repulsion.editingFinished.connect(number_save)

        max_iter = QtWidgets.QSpinBox()
        max_iter.setSingleStep(1)
        max_iter.setRange(1, self.max_iter)
        max_iter.setValue(self.options['max_iter'])
        max_iter.editingFinished.connect(number_save)

        form = QtWidgets.QFormLayout()

        form.addRow("&Размерность задачи", dimension)
        form.addRow("&Частицы находятся в матрице", variant)
        form.addRow("&Определение фракций", definition)
        form.addRow("Размер &матрицы", matrix)
        form.addRow("&Зазор между частицами", gap)
        form.addRow("&Граничное отталкивание (%)", boundary_repulsion)
        form.addRow("Количество &итераций", max_iter)

        self.setLayout(form)

        self.setWindowTitle('Структура модели')
        self.show()
