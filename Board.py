from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
from Figure import Figure, FigureForm
from PyQt5.QtMultimedia import QSound
import os
from copy import deepcopy
from time import sleep


class Board(QMainWindow):
    width = 10
    height = 20

    status = pyqtSignal(str)

    def __init__(self, name):

        app_dir = os.path.dirname(__file__)
        sound_folder = 'sound'
        sound_line = 'success.wav'
        sound_end = 'end.wav'

        self.sounds = {
            'line': QSound(os.path.join(app_dir, sound_folder, sound_line)),
            'end': QSound(os.path.join(app_dir, sound_folder, sound_end))
        }

        self.board = []
        super().__init__()

        self.timer = QBasicTimer()
        self.speed = 390
        self.normal_speed = self.speed
        self.need_acceleration = False

        self.need_animation = False
        self.animation_sleep = False
        self.animation_counter = 0

        self.lines_to_remove = []

        self.need_new_figure = False
        self.cur_x = 0
        self.cur_y = 0
        self.score = 0
        self.is_started = False
        self.is_stopped = False

        self.figure_counter = -1
        self.level = 1

        self.setFocusPolicy(Qt.StrongFocus)
        self.clear()

        self.cur_block = Figure()
        self.next_block = Figure()

        self.result = []
        self.name = name

    def start(self):
        self.is_started = True
        self.need_new_figure = False
        self.score = 0
        self.clear()

        self.status.emit('Score: ' + str(self.score) + '\n' + 'Level ' + str(self.level))

        self.make_new_block(self.cur_block)
        self.try_finish(self.cur_block)
        self.make_new_block(self.next_block)
        self.timer.start(self.speed, self)

    def get_next_level(self):

        if self.speed - 15 > 30:
            self.speed -= 15
            self.level += 1
            self.figure_counter = 0
            self.timer.start(self.speed, self)

    def make_new_block(self, block):

        if self.need_acceleration:
            self.speed = self.normal_speed
            self.need_acceleration = False
            self.timer.start(self.speed, self)

        self.figure_counter += 1
        if self.figure_counter == 5:
            self.get_next_level()

        block.set_random_shape()

    def try_finish(self, block):

        self.cur_x = int(Board.width / 2)
        self.cur_y = Board.height + block.min_y() - 1

        if not self.try_move(block, self.cur_x, self.cur_y):
            block.set_shape(FigureForm.Empty)

            self.is_started = False
            self.timer.stop()
            self.sounds['end'].play()
            self.status.emit('Game is over. Your score: ' + str(self.score))
            self.write_result()
            self.update()

    def try_move(self, new_block, new_x, new_y):

        for i in range(4):
            x = new_x + new_block.x(i)
            y = new_y - new_block.y(i)
            if self.is_stopped or x < 0 or x >= Board.width or y < 0 \
                    or y >= Board.height \
                    or self.get_shape_at(x, y) != FigureForm.Empty:
                return False

        self.cur_block = new_block
        self.cur_x = new_x
        self.cur_y = new_y
        self.update()
        return True

    def get_shape_at(self, x, y):
        return self.board[(y * Board.width) + x]

    def set_shape_at(self, x, y, form):
        self.board[(y * Board.width) + x] = form

    def get_square_width(self):
        return 70

    def get_square_height(self):
        return 70

    def write_result(self):

        with open('results.txt', 'a', encoding='utf-8') as f:
            f.write(self.name + ' ' + str(self.score) + '\n')

        with open('results.txt', 'r', encoding='utf-8') as f:
            input = f.read()

        lines = input.split('\n')
        lines.pop()
        list = []
        for l in lines:
            name, score = l.split(' ')
            list.append((name, score))

        list.sort(key=lambda x: int(x[1]), reverse=True)
        self.result = list

    def draw_results(self, painter):

        painter.fillRect(0, 0, 10000, 10000, QColor('white'))
        painter.drawText(10, 10, 500, 500, Qt.AlignLeft,
                         'Best 10\n\nSCORE TABLE')
        count = 1

        for i in range(len(self.result)):
            painter.drawText(100, 70 * (i + 5) + 300, 500, 500,
                             Qt.AlignLeft, self.result[i][0])
            painter.drawText(450, 70 * (i + 5) + 300, 5000000, 500,
                             Qt.AlignLeft, self.result[i][1])
            if count == 10:
                break
            count += 1

    def draw_board(self, painter):
        pen = QPen(Qt.white, 2, Qt.DashLine)
        painter.setPen(pen)

        for i in range(10):
            painter.drawLine(70 * (i + 1), 50, 70 * (i + 1), 1700)

        painter.fillRect(750, 50, 400, 400, QColor(1111))

        for x, y in self.next_block.coord:
            form = self.next_block.form()
            if form != FigureForm.Empty:
                self.draw_square(painter, x * 70 + 910, y * 70 + 190, form)

    def paintEvent(self, event):

        painter = QPainter(self)
        rect = self.contentsRect()
        painter.fillRect(0, 50, 700, 1700, QColor(1111))

        if self.need_animation:

            self.draw_board(painter)
            board_top = rect.bottom() - Board.height * self.get_square_height()

            if self.cur_block.form() != FigureForm.Empty:
                self.draw_curr_block(painter, rect, board_top)

            self.draw_animation(painter, rect, board_top)
            self.need_animation = False

        elif not self.is_started:
            self.draw_results(painter)

        else:
            self.draw_board(painter)
            board_top = rect.bottom() - Board.height * self.get_square_height()
            self.draw_blocks(painter, rect, board_top)
            if self.cur_block.form() != FigureForm.Empty:
                self.draw_curr_block(painter, rect, board_top)

    def draw_blocks(self, painter, rect, board_top):

        """
                for m in self.lines_to_remove:
            for k in range(m, Board.height):
                for l in range(Board.width):
                    self.set_shape_at(l, k, self.get_shape_at(l, k + 1))
        self.lines_to_remove=[]
        """
        for i in range(Board.height):
            for j in range(Board.width):
                form = self.get_shape_at(j, Board.height - i - 1)

                if form != FigureForm.Empty:
                    self.draw_square(painter,
                                     rect.left() + j * self.get_square_width(),
                                     board_top + i * self.get_square_height(),
                                     form)

    def draw_animation(self, painter, rect, board_top):

        for i in range(Board.height):
            for j in range(Board.width):
                form = self.get_shape_at(j, Board.height - i - 1)

                if form != FigureForm.Empty:
                    if Board.height - i - 1 in self.lines_to_remove:
                        form = 8
                    self.draw_square(painter,
                                     rect.left() + j * self.get_square_width(),
                                     board_top + i * self.get_square_height(),
                                     form)

        for i in self.lines_to_remove:
            for j in range(Board.width):
                self.draw_square(painter,
                                 rect.left() + j * self.get_square_width(),
                                 board_top + (Board.height - i - 1) * self.get_square_height()
                                 + self.animation_counter * 10,
                                 8)
                self.draw_square(painter,
                                 rect.left() + j * self.get_square_width(),
                                 board_top + (Board.height - i - 1) * self.get_square_height(),
                                 9)

    def draw_curr_block(self, painter, rect, board_top):
        for i in range(4):
            x = self.cur_x + self.cur_block.x(i)
            y = self.cur_y - self.cur_block.y(i)
            self.draw_square(painter,
                             rect.left() + x * self.get_square_width(),
                             board_top + (Board.height - y - 1) * self.get_square_height(),
                             self.cur_block.form())

    def keyPressEvent(self, event):

        if (not self.is_started) or self.cur_block.form() == FigureForm.Empty:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()

        if (not self.is_stopped) and key == Qt.Key_Right:
            self.try_move(self.cur_block, self.cur_x + 1, self.cur_y)

        elif (not self.is_stopped) and key == Qt.Key_Left:
            self.try_move(self.cur_block, self.cur_x - 1, self.cur_y)

        elif (not self.is_stopped) and key == Qt.Key_Up:
            self.try_move(self.cur_block.rotate(), self.cur_x, self.cur_y)
        elif (not self.is_stopped) and key == Qt.Key_Down:
            self.drop_down()
        elif key == Qt.Key_Space:
            self.is_stopped = not self.is_stopped
        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):

        if self.animation_sleep:
            sleep(0.15)
            self.is_stopped = False
            self.animation_sleep = False

        if event.timerId() == self.timer.timerId():

            if self.need_new_figure and not self.is_stopped:
                self.need_new_figure = False
                self.cur_block = deepcopy(self.next_block)
                self.make_new_block(self.next_block)
                self.try_finish(self.cur_block)
            elif not self.is_stopped:
                self.down()

        else:
            super(Board, self).timerEvent(event)

    def clear(self):

        for i in range(Board.height * Board.width):
            self.board.append(FigureForm.Empty)

    def down(self):

        if not self.try_move(self.cur_block, self.cur_x, self.cur_y - 1):
            self.block_dropped()

    def block_dropped(self):

        for i in range(4):
            x = self.cur_x + self.cur_block.x(i)
            y = self.cur_y - self.cur_block.y(i)
            self.set_shape_at(x, y, self.cur_block.form())

        self.remove_line()

        if not self.need_new_figure:
            self.cur_block = deepcopy(self.next_block)
            self.make_new_block(self.next_block)
            self.try_finish(self.cur_block)

    def get_lines_to_remove(self):

        lines_to_remove = []

        for i in range(Board.height):
            n = 0
            for j in range(Board.width):
                if not self.get_shape_at(j, i) == FigureForm.Empty:
                    n = n + 1
            if n == 10:
                lines_to_remove.append(i)
                self.need_animation = True

        lines_to_remove.reverse()
        self.lines_to_remove = lines_to_remove

    def remove_line(self):
        self.get_lines_to_remove()

        count = 0

        count += len(self.lines_to_remove)
        if count > 0:
            self.update_data(count)

            self.is_stopped = True
            self.animation_sleep = True

            self.update()

            for m in self.lines_to_remove:
                for k in range(m, Board.height):
                    for l in range(Board.width):
                        self.set_shape_at(l, k, self.get_shape_at(l, k + 1))

    def update_data(self, count):
        self.sounds['line'].play()

        self.score = self.score + count
        self.status.emit('Score: ' + str(self.score)
                         + '\n' + 'Level ' + str(self.level))

        self.need_new_figure = True
        self.cur_block.set_shape(FigureForm.Empty)
        self.update()

    def draw_square(self, painter, x, y, form):

        colors = [QColor(0x000000), QColor(0x66CCCC), QColor(0x66CC66), QColor(0xCC66CC),
                  QColor(0xCCCC66), QColor(0x6666CC), QColor(0xCC6666), QColor(0xDAAA00), QColor(1111),
                  QColor('red')]
        color = colors[form]

        painter.fillRect(x + 1, y + 1, self.get_square_width() - 2,
                         self.get_square_height() - 2, color)

    def drop(self):

        new_y = self.cur_y
        while new_y > 0:
            if not self.try_move(self.cur_block, self.cur_x, new_y - 1):
                break
            new_y -= 1

        self.block_dropped()

    def drop_down(self):
        if not self.need_acceleration:
            self.normal_speed = self.speed
        self.need_acceleration = True
        if self.speed - 100 > 0:

            self.speed -= 100
            self.timer.start(self.speed, self)

        else:
            self.drop()
