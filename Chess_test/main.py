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

board_notation = 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4' #Place FEN board notation
chessBoard = chess.Board(board_notation)
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
            stockfishMovesList.append(str(chessBoard.parse_san(inputText)))
            chessBoard.push_san(inputText)

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
            self.count = self.count + 1
            self.keepPlaying = self.UUAIPlays()

            if self.keepPlaying is True:
                self.count = self.count + 1
                self.keepPlaying = self.PlayerPlays()



    def UUAIPlays(self):
        # First we play(WHITE)
        computer_color = 'w'
        if len(stockfishMovesList) == 0:
            move = 'None'
            position = chess.STARTING_FEN
        else:
            move = stockfishMovesList[len(stockfishMovesList) - 1]
            position = chessBoard.fen()

        if board_notation != '':
            position = board_notation

        best_move = engine.Engine(move, position, computer_color)
        # engine.Node(chessBoard)
        # move = best_move.build_output_data()
        boarde = engine.Node(chessBoard)
        move = boarde.best_moves[0][0]
        self.chessWindow.playMove(move, "UUAI")
        return self.endOfGameCheck("WHITE")

    def PlayerPlays(self):
        # Then the bot plays(BLACK)
        # stockfish.set_position(stockfishMovesList)
        # bestMove = stockfish.get_best_move()
        #
        # while chess.Move.from_uci(bestMove) in chessBoard.legal_moves is False:
        #     bestMove = stockfish.get_best_move()
        #
        # self.chessWindow.playMove(bestMove, "Stockfish")
        legalMove = False

        while legalMove is False:
            try:
                playerInput = input()
                chessBoard.parse_san(playerInput)
                legalMove = True
            except:
                print("Illegal move try again")

        self.chessWindow.playMove(playerInput, "Player")
        return self.endOfGameCheck("BLACK")

    def endOfGameCheck(self, player):
        if chessBoard.is_checkmate():
            print(player, "WINS!")
            print("Move count", self.count)
            return False
        elif chessBoard.is_insufficient_material():
            print("IT IS A STALEMATE")
            print("Move count", self.count)
            return False
        elif chessBoard.is_game_over():
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
