#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Модуль создания неупорядоченного распределения частиц
"""

import numpy as np
from PyQt5 import QtWidgets
import shapes
import fill_deg


def check_boundary(app, particle):
    """
    Проверить близость границ частицы и матрицы.

    расстояния от центра частицы:
    distance - ... до ближайшей границы матрицы по данной координате;
    cross - ... "внутрь";
    gap - ... "наружу";

    """

    cross = particle.d / 2 -\
        app.options['boundary_repulsion'] / 100 * particle.d / 2
    gap = particle.d / 2 +\
        app.options['boundary_repulsion'] / 100 * particle.d / 2
    middle = app.options['matrix'] / 2

    coordinates = sorted(particle.__dict__.keys())
    coordinates.remove('d')

    for i in coordinates:
        if particle.__getattribute__(i) < middle:
            distance = particle.__getattribute__(i)
        else:
            distance = app.options['matrix'] - particle.__getattribute__(i)

        if cross < distance < gap:
            print("Частица отсеяна ввиду близости"
                  "внешней границы с границей матрицы")
            print(particle)
            print(
                'coordinate={0}, distance={1:.3f}, cross={2:.3f}, gap={3:.3f}'.
                format(i, distance, cross, gap))
            print('-' * 70)
            return True
            # недопустимо близко к границе матрицы
            # (хотя бы по одной координате)

    return False


def intersection(app, first, second):
    """
    Определение факта пересечения двух частиц.

    first - первая частица;
    second - вторая частица.

    """

    coordinates = sorted(first.__dict__.keys())
    coordinates.remove('d')

    value = 0
    for i in coordinates:
        value += np.square(
            second.__getattribute__(i) - first.__getattribute__(i))

    distance = np.sqrt(value)

    if distance > (first.d / 2 + second.d / 2 + app.options['gap']):
        overlap = False  # не пересекаются (с учетом зазора)
    else:
        overlap = True  # пересекаются или касаются

    return overlap


def print_to_console(app, event, particle=None):
    """Сообщение в текстовую консоль."""

    if event == 'new':
        app.processStart.setDisabled(True)
        app.processStop.setEnabled(True)

        app.random_particles = app.all_particles.copy()
        # учёт загруженных из файлов частиц

        app.textEdit.clear()  # очистить консоль

        text = '<font color="blue"><b>Новый расчёт</b></font><br>'

        text += 'Рабочий каталог: {0}<br>'.format(app.work_dir)

        if app.loaded_files:
            text += 'Загружен(-ы) файл(-ы) распределения частиц:<br>'
            for file in app.loaded_files:
                text += '{0}<br>'.format(file.split("/")[-1])

        text += 'Размерность задачи = {0}<br>'.format(
            app.options['dim_tup'][app.options['dim_ind']])
        text += 'Частицы находятся в матрице = {0}<br>'.format(
            app.options['var_tup'][app.options['var_ind']])
        text += 'Определение фракций = {0}<br>'.format(
            app.options['def_tup'][app.options['def_ind']])
        text += 'Размер матрицы = {0}<br>'.format(app.options['matrix'])
        text += 'Зазор между частицами = {0}<br>'.format(app.options['gap'])
        text += 'Граничное отталкивание (%) = {0}<br>'.format(
            app.options['boundary_repulsion'])
        text += 'Количество итераций = {0}<br>'.format(app.options['max_iter'])
        text += 'Распределение частиц = {0}<br>'.format(
            app.options['fractions_definition'])

    elif event == 'added':
        text = '<font color="green">Частица добавлена</font>'

    elif event == 'overlap':
        text = '<font color="purple">Мешает: ({0})</font>'.format(particle)

    else:
        text = 'Ошибка! Неизвестное событие для вывода в текстовую консоль.'

    QtWidgets.qApp.processEvents()
    app.message(text)


def preset_particles_number(app):
    """Создать распределение частиц по известному их количеству."""

    print_to_console(app, 'new')
    fails = {}  # не удалось подобрать координаты частицы

    app.processRunning = True
    for diameter, remain in app.options['fractions_definition']:
        if diameter != 0:
            while app.processRunning and remain > 0:
                # осталось разместить частиц данного диаметра
                app.message('<font color="blue">Осталось разместить:</font> \
                            <font color="teal">кол-во = {0}, \
                            диаметр = {1:.1f}</font>'.format(remain, diameter))
                current_iteration = 1
                # кол-во попыток подобрать распределение частиц в матрице
                while current_iteration < app.options['max_iter']:

                    if app.options['dim_ind'] == 0:  # 2D
                        point = shapes.Point2D()
                    elif app.options['dim_ind'] == 1:  # 3D
                        point = shapes.Point3D()

                    if app.options['var_ind'] == 0:
                        # частицы целиком находятся в матрице
                        point.randomize_particles_inside(
                            app.options['matrix'], diameter)
                    elif app.options['var_ind'] == 1:
                        # центры частиц находятся в матрице
                        point.randomize_centers_inside(app.options['matrix'])

                    QtWidgets.qApp.processEvents()
                    if app.processRunning:
                        app.message('Итерация {0}: ({1})'.format(
                            current_iteration, point))
                        app.current_event_label.setText(
                            'диаметр = {0:.1f}; осталось разместить = {1:.0f};\
                             итерация = {2}'.format(
                                 diameter, remain, current_iteration))
                    else:
                        break

                    if app.options['dim_ind'] == 0:  # 2D
                        particle = shapes.Circle(point.x, point.y, diameter)
                    elif app.options['dim_ind'] == 1:  # 3D
                        particle = shapes.Sphere(
                            point.x, point.y, point.z, diameter)

                    # проверка кол-ва пересечения границ
                    # (допускается только одно!)
                    if particle.crossing(matrix_edge=app.options['matrix'])\
                            > 1:
                        continue

                    # проверка близости границ
                    if check_boundary(app, particle):
                        # недопустимо близко к границе
                        current_iteration += 1
                        continue

                    # добавление первой частицы
                    if not app.random_particles:
                        app.random_particles.append(particle)
                        print_to_console(app, 'added')
                        break

                    # добавление остальных частиц
                    intersec = False  # пересечение частиц
                    for i in app.random_particles:
                        if intersection(app, particle, i):
                            print_to_console(app, 'overlap', i)
                            intersec = True  # установлено пересечение частиц
                            break
                    if not intersec:
                        app.random_particles.append(particle)
                        print_to_console(app, 'added')
                        break
                    else:
                        current_iteration += 1
                else:
                    if diameter in fails:
                        fails[diameter] += 1
                    else:
                        fails[diameter] = 1
                    app.message(
                        '<font color="red">Не удалось добавить \
                        частицу диаметра {0}</font>'.format(diameter))

                remain -= 1

        else:
            continue
    if app.processRunning:
        if fails:
            app.message(
                '<font color="red"><b>Не добавлены частицы:</b></font>')
            for diameter in fails:
                app.message(
                    '<font color="red">диаметр = {0:.1f}, \
                    кол-во = {1}</font>'.format(diameter, fails[diameter]))
        else:
            app.message(
                '<font color="blue"><b>Все частицы \
                успешно добавлены</b></font>')

        app.all_particles = app.random_particles.copy()
        # обновление общего набора частиц
        app.saveAll.setEnabled(True)
    else:
        app.message(
            '<font color="red"><b>Процесс расчёта \
            остановлен пользователем</b></font>')

    app.processStart.setEnabled(True)
    app.processStop.setDisabled(True)
    app.cleanDistributions.setEnabled(True)

    app.current_event_label.setText('')


def preset_filling_degree(app):
    """Создать распределение частиц по известной степени заполнения фракций."""

    def fil():
        if app.options['dim_ind'] == 0:  # 2D
            m = shapes.SquareMatrix(app.options['matrix'])
        elif app.options['dim_ind'] == 1:  # 3D
            m = shapes.CubeMatrix(app.options['matrix'])

        s = fill_deg.space(matrix=m, particle=particle)
        f = fill_deg.filling(matrix=m, space_=s)

        return f

    print_to_console(app, 'new')

    app.processRunning = True
    for diameter, max_filling in app.options['fractions_definition']:
        if diameter != 0:
            current_filling = 0
            current_iteration = 1
            # кол-во попыток подобрать распределение частиц в матрице

            while app.processRunning and current_filling < max_filling and\
                    current_iteration < app.options['max_iter']:
                app.message('<font color="teal">текущее заполнение = {0:.3f}, \
                            диаметр = {1:.1f}</font>'.format(
                                current_filling, diameter))

                if app.options['dim_ind'] == 0:  # 2D
                    point = shapes.Point2D()
                elif app.options['dim_ind'] == 1:  # 3D
                    point = shapes.Point3D()

                if app.options['var_ind'] == 0:
                    # частицы целиком находятся в матрице
                    point.randomize_particles_inside(
                        app.options['matrix'], diameter)
                elif app.options['var_ind'] == 1:
                    # центры частиц находятся в матрице
                    point.randomize_centers_inside(app.options['matrix'])

                QtWidgets.qApp.processEvents()
                if app.processRunning:
                    app.message(
                        'Итерация {0}: ({1})'.format(current_iteration, point))
                    app.current_event_label.setText(
                        'диаметр = {0:.1f}; текущее заполнение = {1:.3f}; \
                        итерация = {2}'.format(
                            diameter, current_filling, current_iteration))
                else:
                    break

                if app.options['dim_ind'] == 0:  # 2D
                    particle = shapes.Circle(point.x, point.y, diameter)
                elif app.options['dim_ind'] == 1:  # 3D
                    particle = shapes.Sphere(
                        point.x, point.y, point.z, diameter)

                # проверка кол-ва пересечения границ (допускается только одно!)
                if particle.crossing(matrix_edge=app.options['matrix']) > 1:
                    current_iteration += 1
                    continue

                # проверка близости границ
                if check_boundary(app, particle):
                    # недопустимо близко к границе
                    current_iteration += 1
                    continue

                # добавление первой частицы
                if not app.random_particles:
                    app.random_particles.append(particle)
                    print_to_console(app, 'added')
                    current_filling += fil()
                    continue

                # добавление остальных частиц
                intersec = False  # пересечение частиц
                for i in app.random_particles:
                    if intersection(app, particle, i):
                        print_to_console(app, 'overlap', i)
                        intersec = True  # установлено пересечение частиц
                        current_iteration += 1
                        continue
                if not intersec:
                    app.random_particles.append(particle)
                    print_to_console(app, 'added')
                    current_filling += fil()
                    continue
                else:
                    current_iteration += 1

        else:
            continue

    if app.processRunning:
        app.message(
            '<font color="blue"><b>Все частицы успешно добавлены</b></font>')

        app.all_particles = app.random_particles.copy()
        # обновление общего набора частиц
        app.saveAll.setEnabled(True)
    else:
        app.message(
            '<font color="red"><b>Процесс расчёта \
            остановлен пользователем</b></font>')

    app.processStart.setEnabled(True)
    app.processStop.setDisabled(True)
    app.cleanDistributions.setEnabled(True)

    app.current_event_label.setText('')
