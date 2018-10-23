import random


class FigureForm(object):
    Empty = 0
    Zform = 1
    Sform = 2
    Line = 3
    Tform = 4
    Square = 5
    Lform = 6
    Jform = 7
    RLine = 8


class Figure(object):
    coord_table = (
        ((0, 0), (0, 0), (0, 0), (0, 0)),
        ((0, -1), (0, 0), (-1, 0), (-1, 1)),
        ((0, -1), (0, 0), (1, 0), (1, 1)),
        ((0, -1), (0, 0), (0, 1), (0, 2)),
        ((-1, 0), (0, 0), (1, 0), (0, 1)),
        ((0, 0), (1, 0), (0, 1), (1, 1)),
        ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ((1, -1), (0, -1), (0, 0), (0, 1)),
        ((0, 0), (0, 0), (0, 0), (0, 0))
    )

    def __init__(self):

        self.coord = [[0, 0] for i in range(4)]
        self.block_shape = FigureForm.Empty

        self.set_shape(FigureForm.Empty)

    def form(self):
        return self.block_shape

    def set_shape(self, form):

        table = Figure.coord_table[form]

        for i in range(4):
            for j in range(2):
                self.coord[i][j] = table[i][j]

        self.block_shape = form

    def set_random_shape(self):
        self.set_shape(random.randint(1, 7))

    def x(self, index):
        return self.coord[index][0]

    def y(self, index):
        return self.coord[index][1]

    def set_x(self, index, x):
        self.coord[index][0] = x

    def set_y(self, index, y):
        self.coord[index][1] = y

    def min_y(self):

        m = self.coord[0][1]
        for i in range(4):
            m = min(m, self.coord[i][1])

        return m

    def rotate(self):

        if self.block_shape == FigureForm.Square:
            return self

        result = Figure()
        result.block_shape = self.block_shape

        for i in range(4):
            result.set_x(i, self.y(i))
            result.set_y(i, -self.x(i))

        return result
