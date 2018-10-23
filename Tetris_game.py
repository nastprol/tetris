import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from Board import Board
from PyQt5.QtWidgets import QLineEdit, QPushButton, QLabel, QSpinBox


class Form(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(300, 300)

        self.name = ""

        self.lbl_name = QLabel("Enter your name", self)
        self.lbl_name.move(20, 100)
        self.lbl_name.resize(480, 70)
        self.name_box = QLineEdit(self)
        self.name_box.move(20, 200)
        self.name_box.resize(480, 70)

        self.button = QPushButton('START', self)
        self.button.move(20, 300)
        self.button.resize(480, 70)
        self.button.clicked.connect(self.on_click)

    def on_click(self):

        self.name = self.name_box.text()
        self.close()
        self.game = Game(self.name)


class Game(QMainWindow):

    def __init__(self, name):
        super().__init__()

        self.board = Board(name)
        self.setCentralWidget(self.board)
        self.statusbar = self.statusBar()
        self.board.status[str].connect(self.statusbar.showMessage)
        self.board.start()
        self.resize(1500, 1500)
        self.show()


class Start(QMainWindow):

    def __init__(self):
        super().__init__()
        self.form = Form()

        self.form.setGeometry(100, 100, 2000, 1500)
        self.form.show()


if __name__ == '__main__':
    app = QApplication([])
    start = Start()
    sys.exit(app.exec_())
