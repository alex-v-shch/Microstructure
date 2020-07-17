#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль редактирования фракций
"""

from PyQt5 import QtWidgets


class EditFractions(QtWidgets.QDialog):
    """Диалог редактирования фракций."""

    def __init__(self, message, options):
        super().__init__()
        self.message = message
        self.options = options

        self.setWindowTitle('Фракции')

        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setRowCount(len(self.options['fractions_definition']))
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Диаметр", "Определение"])

        # заполнение массива
        for num, i in enumerate(self.options['fractions_definition']):
            self.table_widget.setItem(
                num, 0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.table_widget.setItem(
                num, 1, QtWidgets.QTableWidgetItem(str(i[1])))

        self.button_widget_1 = QtWidgets.QPushButton("Добавить ряд")
        self.button_widget_2 = QtWidgets.QPushButton("Удалить ряд")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.table_widget)
        self.layout.addWidget(self.button_widget_1)
        self.layout.addWidget(self.button_widget_2)
        self.setLayout(self.layout)

        self.show()

        self.table_widget.cellChanged.connect(self.changed)
        self.button_widget_1.clicked.connect(self.add_row)
        self.button_widget_2.clicked.connect(self.del_row)

    def changed(self):

        for current_qtable_widget_item in self.table_widget.selectedItems():
            self.options[
                'fractions_definition'][current_qtable_widget_item.row()][
                    current_qtable_widget_item.column()] = float(
                        current_qtable_widget_item.text())

    def add_row(self):
        """Add row."""

        self.table_widget.insertRow(len(self.options['fractions_definition']))
        self.options['fractions_definition'].append([0, 0])

    def del_row(self):
        """Del row."""

        self.table_widget.removeRow(
            len(self.options['fractions_definition']) - 1)
        self.options['fractions_definition'].pop(-1)
