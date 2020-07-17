#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль визуализации данных
"""

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


class View:
    """Вид"""

    def __init__(self, data, matrix_edge):
        self.data = data
        self.matrix_edge = matrix_edge
        self.array = None
        self.circles_options = {
            'fill': True, 'edgecolor': 'black', 'facecolor': 'orange',
            'alpha': 0.7}

        self.data_preparation()

    def data_preparation(self):
        data_list = []
        for i in self.data:
            if 'z' in i.__dict__:  # 3D
                data_list.append((i.x, i.y, i.z, i.d))
            else:  # 2D
                data_list.append((i.x, i.y, 0., i.d))

        self.array = np.array(
            data_list, dtype=[
                ('x', np.float64), ('y', np.float64),
                ('z', np.float64), ('d', np.float64)])

    def limits(self):
        plt.xlim(0, self.matrix_edge)
        plt.ylim(0, self.matrix_edge)

    def labels(self, abscissa='', ordinate=''):
        plt.xlabel(abscissa)
        plt.ylabel(ordinate)


class FrontView(View):
    """Вид спереди (x-y)"""

    def __init__(self, axes, data, matrix_edge):
        super().__init__(data, matrix_edge)

        self.ax = axes

        self.limits()
        self.labels(abscissa='X', ordinate='Y')

        self.array.sort(order='z')

        for x, y, _, d in self.array:
            cir = patches.Circle((x, y), radius=d/2, **self.circles_options)
            self.ax.add_patch(cir)


class RightView(View):
    """Вид справа (y-z)"""

    def __init__(self, axes, data, matrix_edge):
        super().__init__(data, matrix_edge)

        self.ax = axes

        self.limits()
        self.labels(abscissa='Y', ordinate='Z')

        self.array.sort(order='x')

        for _, y, z, d in self.array:
            cir = patches.Circle((y, z), radius=d/2, **self.circles_options)
            self.ax.add_patch(cir)


class TopView(View):
    """Вид сверху (z-x)"""

    def __init__(self, axes, data, matrix_edge):
        super().__init__(data, matrix_edge)

        self.ax = axes

        self.limits()
        self.labels(abscissa='Z', ordinate='X')

        self.array.sort(order='y')

        for x, _, z, d in self.array:
            cir = patches.Circle((z, x), radius=d/2, **self.circles_options)
            self.ax.add_patch(cir)


class View3D:
    """View3D."""

    def __init__(self, edge, data):
        plt.close('all')
        fig = plt.figure(num='Микроструктура', figsize=(7, 7), dpi=100)

        ax1 = fig.add_subplot(2, 2, 1)
        RightView(axes=ax1, data=data, matrix_edge=edge)

        ax2 = fig.add_subplot(2, 2, 2)
        FrontView(axes=ax2, data=data, matrix_edge=edge)

        ax3 = fig.add_subplot(2, 2, 4)
        TopView(axes=ax3, data=data, matrix_edge=edge)

        plt.tight_layout()
        plt.show()


class View2D:
    """View2D."""

    def __init__(self, edge, data):
        plt.close('all')
        plt.figure(num='Микроструктура', figsize=(7, 7), dpi=100)

        ax = plt.axes()
        FrontView(axes=ax, data=data, matrix_edge=edge)

        plt.tight_layout()
        plt.show()


if __name__ == '__main__':

    import shapes

    m = shapes.CubeMatrix(edge=100.)

    p1 = shapes.Sphere(x=0., y=20., z=40., d=10.)
    p2 = shapes.Sphere(x=50., y=50., z=50., d=20.)

    View3D(m.edge, [p1, p2])

    p3 = shapes.Circle(x=10., y=40, d=30.)
    p4 = shapes.Circle(x=50., y=75., d=15.)

    View2D(m.edge, [p3, p4])
