import chess
import chess.svg
import os

from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from stockfish import Stockfish
import engine

stockfish = Stockfish("stockfish_20090216_x64_bmi2.exe")
stockfish.set_skill_level(0) #this goes from 0 to 20

chessBoard = chess.Board()
stockfishMovesList = []


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

    def playMove(self, inputText, player):
        if player == "UUAI":
            stockfishMovesList.append(str(inputText))
            chessBoard.push(chess.Move.from_uci(str(inputText)))
        else:
            stockfishMovesList.append(inputText)
            chessBoard.push(chess.Move.from_uci(inputText))

        self.updateWindow()

class Terminal(QRunnable):
    chessWindow = None
    keepPlaying = None
    textDisplayed = None
    count = 0

    def __init__(self, window):
        super().__init__()
        self.chessWindow = window
        self.keepPlaying = True
        self.textDisplayed = False
        self.count = 0

    def run(self):
        self.runGame()

    def runGame(self):
        while self.keepPlaying is True:
            self.keepPlaying = self.UUAIPlays()
            self.count = self.count + 1

            if self.keepPlaying is True:
                self.keepPlaying = self.StockfishPlays()
                self.count = self.count + 1

    def UUAIPlays(self):
        # First we play(WHITE)
        # legalMove = False
        #
        # while legalMove is False:
        #     try:
        #         playerInput = input()
        #         chessBoard.parse_san(playerInput)
        #         legalMove = True
        #     except:
        #         print("Illegal move try again")

        computer_color = 'w'
        if len(stockfishMovesList) == 0:
            move = 'None'
            position = chess.STARTING_FEN
        else:
            move = stockfishMovesList[len(stockfishMovesList) - 1]
            position = chessBoard.fen()

        engine.Engine(move, position, computer_color)
        moves = engine.Node(chessBoard)
        best_move = moves.best_moves[0][0]
        self.chessWindow.playMove(best_move, "UUAI")
        return self.endOfGameCheck("WHITE")

    def StockfishPlays(self):
        # Then the bot plays(BLACK)
        stockfish.set_position(stockfishMovesList)
        bestMove = stockfish.get_best_move()

        while chess.Move.from_uci(bestMove) in chessBoard.legal_moves is False:
            bestMove = stockfish.get_best_move()

        self.chessWindow.playMove(bestMove, "Stockfish")
        return self.endOfGameCheck("BLACK")

    def endOfGameCheck(self, player):
        if chessBoard.is_checkmate():
            print(player, "WINS!")
            print("Move count", self.count)
            return False
        elif chessBoard.is_insufficient_material():
            print("IT IS A DRAW")
            print("Move count", self.count)
            return False
        else:
            return True

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
