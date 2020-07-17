#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль определения степени заполнения матрицы частицами наполнителя (3D)
"""

import numpy as np


def _location(matrix, particle):
    """Определение места расположения частицы относительно матрицы."""

    loc = [None, None]

    try:
        if particle.d > matrix.edge:
            raise RuntimeError("Диаметр частицы превышает размер матрицы!")

        if particle.x + particle.d / 2 > matrix.edge:
            loc[0] = 1
        elif particle.x - particle.d / 2 < 0:
            loc[0] = -1
        else:
            loc[0] = 0

        if particle.y + particle.d / 2 > matrix.edge:
            loc[1] = 1
        elif particle.y - particle.d / 2 < 0:
            loc[1] = -1
        else:
            loc[1] = 0

        if 'z' in particle.__dict__:
            loc = loc + [None]
            if particle.z + particle.d / 2 > matrix.edge:
                loc[2] = 1
            elif particle.z - particle.d / 2 < 0:
                loc[2] = -1
            else:
                loc[2] = 0

        return loc

    except RuntimeError as error:
        print(error)


def space(matrix, particle):
    """Определение площади либо объёма частицы."""

    loc = _location(matrix=matrix, particle=particle)

    height = 0

    if loc[0] == 1:
        height = particle.x + particle.d / 2 - matrix.edge
    elif loc[0] == -1:
        height = abs(particle.x - particle.d / 2)

    if loc[1] == 1:
        height = particle.y + particle.d / 2 - matrix.edge
    elif loc[1] == -1:
        height = abs(particle.y - particle.d / 2)

    if 'z' in particle.__dict__:
        if loc[2] == 1:
            height = particle.z + particle.d / 2 - matrix.edge
        elif loc[2] == -1:
            height = abs(particle.z - particle.d / 2)

    if 'z' in particle.__dict__:
        value = 4 / 3 * np.pi * (particle.d / 2) ** 3 -\
            np.pi * height ** 2 * (particle.d / 2 - height / 3)
    else:
        alpha = 2 * np.arccos(1 - height / (particle.d / 2))
        value = np.pi * (particle.d / 2) ** 2 -\
            0.5 * (particle.d / 2) ** 2 * (alpha - np.sin(alpha))

    return value


def filling(matrix, space_):
    """Степень заполнения матрицы частицами."""

    return space_ / matrix.space()


if __name__ == '__main__':

    import shapes

    square = shapes.SquareMatrix(edge=5.)
    print(square)
    circle = shapes.Circle(x=2.5, y=2.5, d=2.)
    print(circle)
    print('S={0:.3f}'.format(space(square, circle)))
    print('KV={0:.3f}'.format(filling(square, space(square, circle))))

    print('-'*50)

    cube = shapes.CubeMatrix(edge=5.)
    print(cube)
    sphere = shapes.Sphere(x=2.5, y=2.5, z=2.5, d=2.)
    print(sphere)
    print('V={0:.3f}'.format(space(cube, sphere)))
    print('KV={0:.3f}'.format(filling(cube, space(cube, sphere))))
