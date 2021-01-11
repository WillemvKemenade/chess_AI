import chess
import chess.svg

from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from stockfish import Stockfish

# stockfish = Stockfish("stockfish_20090216_x64_bmi2.exe")
# stockfish.set_skill_level(20) #this goes from 0 to 20
#
# stockfish.set_position(["e2e4", "e7e6", "f2f4", "f8c5"]) #this sets all the positions that have been played/ make sure to put in the entire list not piece by piece
# print(stockfish.get_board_visual()) #prints out the board but we probably don't need this
# print(stockfish.get_best_move()) #This gives the best move for the current board setup

chessBoard = chess.Board()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 780, 780)

        self.updateWindow()

    def updateWindow(self):
        self.chessboardSvg = chess.svg.board(chessBoard).encode("UTF-8")
        self.widgetSvg.load(self.chessboardSvg)

    def playMove(self, inputText):
        print(inputText)
        chessBoard.push_san(inputText)
        self.updateWindow()

class Terminal(QRunnable):
    chessWindow = None
    def __init__(self, window):
        super().__init__()
        self.chessWindow = window

    def run(self):
        while True:
            self.chessWindow.playMove(input())

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()

    terminalPlay = Terminal(window)
    QThreadPool.globalInstance().start(terminalPlay)

    app.exec()

    # window.updateWindow()
    # chessBoard.push_san(input())
    # window.updateWindow()
