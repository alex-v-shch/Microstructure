#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Программа генерирует 3D-геометрию в CAE-платформе Salome
"""

from tkinter import (Tk, Toplevel, Menu, Frame, Text, Label, Button, Entry,
                     Scrollbar, END, YES, TOP, RIGHT, LEFT, X, Y, W, BOTH,
                     INSERT)

import csv
import salome
salome.salome_init()
import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()
gg = salome.ImportComponentGUI("GEOM")
import salome_notebook
notebook = salome_notebook.notebook


class Application():
    """Программа."""

    # параметры текстовой консоли
    WIDTH_GUI = 50  # ширина
    HEIGHT_GUI = 20  # высота

    def __init__(self, master):
        master.title('Создание геометрической модели')

        self.options = {
            'dimension': '3D',
            'matrix': 100,
            'work_dir': '/home/vatnik/',
            'file_name': '3D',
            'extension': '.tsv'
        }

        # размерность задачи (2D или 3D), размер матрицы,
        # рабочий каталог, имя файла, расширение имени файла

        self.ORDER = 'dimension', 'matrix', 'work_dir',
        'file_name', 'extension'  # порядок следования

        self.create_widgets(master)

    def msg(self, message):
        """Вывод сообщений в графическую консоль."""

        zap_gui = '$ '
        self.txt.insert(END, zap_gui + message + '\n')
        self.txt.see(INSERT)

    def create_widgets(self, master):
        """Создать виджеты."""

        self.m = Menu(master)
        master.config(menu=self.m)

        self.file_m = Menu(self.m, tearoff=False)
        self.m.add_cascade(label="Меню", menu=self.file_m, underline=0)
        self.file_m.add_command(
            label="Параметры", command=(lambda: self.edit_options()))
        self.file_m.add_separator()
        self.file_m.add_command(
            label="Создать геометрию", command=(lambda: self.creation()))
        self.file_m.add_separator()
        self.file_m.add_command(
            label="Сохранить в файл", command=(lambda: self.save()))

        f = Frame(master)
        f.pack()

        self.txt = Text(
            f, width=self.WIDTH_GUI, height=self.HEIGHT_GUI, font="10")
        sbar = Scrollbar(f)  # полоса прокрутки
        sbar.config(command=self.txt.yview)  # связать с txt
        self.txt.config(yscrollcommand=sbar.set)  # синхронизация виджетов
        sbar.pack(expand=YES, fill=Y, side=RIGHT)
        self.txt.pack(expand=YES, fill=BOTH)

    def edit_options(self):
        """Редактирование параметров."""

        def makeform(t):
            """Форма ввода параметров."""

            entries = []

            for field in self.ORDER:
                row = Frame(t)
                lab = Label(row, width=10, text=field, anchor=W)
                ent = Entry(row, width=50)
                ent.insert(0, self.options[field])
                row.pack(side=TOP, expand=YES, fill=X)
                lab.pack(side=LEFT, expand=YES, fill=X)
                ent.pack(side=RIGHT, expand=YES, fill=X)
                entries.append(ent)
            return entries

        def save(entries):
            """Сохранить параметры."""

            lst = []
            for e in entries:
                lst.append(e.get())

            for j in self.ORDER:
                self.options[j] = lst[self.ORDER.index(j)]
                if j in {'matrix'}:
                    self.options[j] = float(lst[self.ORDER.index(j)])
                else:
                    self.options[j] = str(lst[self.ORDER.index(j)])

            t.destroy()
            self.msg('Параметры сохранены')

        t = Toplevel()
        t.title('Параметры')

        ents = makeform(t)
        Button(t, text='Сохранить',
               command=(lambda: save(ents))).pack(expand=YES, fill=X)

    def creation(self):
        """Создание геометрической модели."""

        data = []
        open_file = self.options['work_dir'] + self.options['file_name'] +\
            self.options['extension']
        with open(open_file, 'r') as f:
            csv_reader = csv.reader(f, delimiter='\t')
            for row in csv_reader:
                row_data = []
                for i in map(float, row):
                    row_data.append(i)
                data.append(row_data)
            self.msg('Загружен файл исходных данных: {0:s}'.format(open_file))

        if self.options['dimension'] == '2D':
            points = []  # точки
            circles = []  # окружности

            # создать прямоугольник в плоскости OXY
            face = geompy.MakeFaceHW(
                self.options['matrix'], self.options['matrix'], 1)

            # переместить прямоугольник
            translation = geompy.MakeTranslation(
                face, self.options['matrix']/2, self.options['matrix']/2, 0)

            # создать окружности
            p0 = geompy.MakeVertex(0., 0., 0.)
            pz = geompy.MakeVertex(0., 0., 1.)
            vz = geompy.MakeVector(p0, pz)

            for d in data:
                (px, py, pz, radius) = d
                point = geompy.MakeVertex(px, py, pz)
                points.append(point)
                circles.append(geompy.MakeCircle(point, vz, radius))

            # создать разбиение
            global partition
            partition = geompy.MakePartition([translation], circles)

            # добавить объекты в проект
            id_face = geompy.addToStudy(face, "Face")
            id_translation = geompy.addToStudy(translation, "Translation")
            id_vector = geompy.addToStudy(vz, "V_Z")

            for number, circle in enumerate(circles):
                id_circle = geompy.addToStudy(
                    circle, "Circle_{0}".format(number))

            id_partition = geompy.addToStudy(partition, "Partition")

            # показать результаты
            gg.createAndDisplayGO(id_partition)
            salome.sg.ViewTop()  # вид сверху

        else:  # 3D
            spheres = []  # шары

            # создать прямоугольный параллелепипед
            box = geompy.MakeBoxDXDYDZ(
                self.options['matrix'], self.options['matrix'],
                self.options['matrix'])

            # создать шары
            for d in data:
                (px, py, pz, radius) = d
                sphere = geompy.MakeSphere(px, py, pz, radius)
                spheres.append(sphere)

            # создать набор геометрических объектов
            global compound
            compound = geompy.MakeCompound([box] + spheres)

            # добавить объекты в проект
            id_box = geompy.addToStudy(box, "Box")

            for number, sphere in enumerate(spheres):
                id_sphere = geompy.addToStudy(
                    sphere, "Sphere_{0}".format(number))

            id_compound = geompy.addToStudy(compound, "Compound")

            # показать результаты
            gg.createAndDisplayGO(id_compound)

    def save(self):
        """Сохранение геометрической модели в файл."""

        if self.options['dimension'] == '2D':
            entity = partition
        else:  # 3D
            entity = compound

        exported_file = self.options['work_dir'] +\
            self.options['file_name'] + '.step'
        geompy.ExportSTEP(entity, exported_file)
        self.msg(
            'Геометрия экспортирована в файл: {0:s}'.format(exported_file))


if __name__ == '__main__':

    root = Tk()
    app = Application(root)
    root.mainloop()
