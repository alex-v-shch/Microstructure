#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль определения форм геометрических объектов
"""

import numpy as np


class SquareMatrix:
    """Матрица в форме квадрата."""

    def __init__(self, edge=1.):
        self.edge = edge

    def __str__(self):
        return 'matrix: square, edge={0:.3f}, space={1:.3f}'.format(
            self.edge, self.space())

    def space(self):
        """Space."""
        return self.edge ** 2


class CubeMatrix(SquareMatrix):
    """Матрица в форме куба."""

    def __init__(self, edge=1.):
        super().__init__(edge)

    def __str__(self):
        return 'matrix: cube, edge={0:.3f}, space={1:.3f}'.format(
            self.edge, self.space())

    def space(self):
        return self.edge ** 3


class Point2D(object):
    """Координаты центра частицы (2D)."""

    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def __str__(self):
        return 'point2d: x={0:.3f}, y={1:.3f}'.format(self.x, self.y)

    def randomize_centers_inside(self, interval):
        self.x = interval * np.random.random_sample()
        self.y = interval * np.random.random_sample()

    def randomize_particles_inside(self, interval, radius):
        self.x = (interval - 4 * radius) * np.random.random_sample() +\
            2 * radius
        self.y = (interval - 4 * radius) * np.random.random_sample() +\
            2 * radius


class Point3D(Point2D):
    """Координаты центра частицы (3D)."""

    def __init__(self, x=0., y=0., z=0.):
        super().__init__(x, y)
        self.z = z

    def __str__(self):
        return 'point3d: x={0:.3f}, y={1:.3f}, z={2:.3f}'.format(
            self.x, self.y, self.z)

    def randomize_centers_inside(self, interval):
        super().randomize_centers_inside(interval)
        self.z = interval * np.random.random_sample()

    def randomize_particles_inside(self, interval, radius):
        super().randomize_particles_inside(interval, radius)
        self.z = (interval - 4 * radius) * np.random.random_sample() +\
            2 * radius


class Circle(Point2D):
    """Частица в форме круга."""

    def __init__(self, x=0., y=0., d=2.):
        super().__init__(x, y)
        self.d = d

    def __str__(self):
        return 'circle: x={0:.3f}, y={1:.3f}, d={2:.3f}'.format(
            self.x, self.y, self.d)

    def space(self):
        return np.pi * (self.d / 2) ** 2

    def crossing(self, matrix_edge):
        """Проверка пересечения границ матрицы"""

        number = 0

        for i in self.x, self.y:
            if i + self.d / 2 > matrix_edge:
                number += 1
            elif i - self.d / 2 < 0:
                number += 1

        return number


class Sphere(Point3D):
    """Частица в форме шара."""

    def __init__(self, x=0., y=0., z=0., d=2.):
        super().__init__(x, y, z)
        self.d = d

    def __str__(self):
        return 'sphere: x={0:.3f}, y={1:.3f}, z={2:.3f}, d={3:.3f}'.format(
            self.x, self.y, self.z, self.d)

    def space(self):
        return 4 / 3 * np.pi * (self.d / 2) ** 3

    def crossing(self, matrix_edge):
        """Проверка пересечения границ матрицы"""

        number = 0

        for i in self.x, self.y, self.z:
            if i + self.d / 2 > matrix_edge:
                number += 1
            elif i - self.d / 2 < 0:
                number += 1

        return number


if __name__ == '__main__':

    sm = SquareMatrix()
    print(sm)

    cm = CubeMatrix()
    print(cm)

    p2d = Point2D()
    print(p2d)

    p3d = Point3D()
    print(p3d)

    c = Circle()
    print(c, c.space(), c.crossing(sm.edge), sep='\n')

    s = Sphere()
    print(s, s.space(), s.crossing(cm.edge), sep='\n')
