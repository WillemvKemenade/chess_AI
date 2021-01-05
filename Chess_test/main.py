import chess
import chess.svg

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget

from stockfish import Stockfish

stockfish = Stockfish("stockfish_20090216_x64_bmi2.exe")
stockfish.set_skill_level(20) #this goes from 0 to 20

stockfish.set_position(["e2e4", "e7e6", "f2f4", "f8c5"]) #this sets all the positions that have been played/ make sure to put in the entire list not piece by piece
print(stockfish.get_board_visual()) #prints out the board but we probably don't need this
print(stockfish.get_best_move()) #This gives the best move for the current board setup

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 780, 780)

        self.chessboard = chess.Board()

        self.chessboardSvg = chess.svg.board(self.chessboard).encode("UTF-8")
        self.widgetSvg.load(self.chessboardSvg)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()