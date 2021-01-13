import chess
import chess.svg

from PyQt5.QtSvg import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from stockfish import Stockfish

stockfish = Stockfish("stockfish_20090216_x64_bmi2.exe")
stockfish.set_skill_level(20) #this goes from 0 to 20

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
            stockfishMovesList.append(str(chessBoard.parse_san(inputText)))
            chessBoard.push_san(inputText)
        else:
            stockfishMovesList.append(inputText)
            chessBoard.push(chess.Move.from_uci(inputText))

        self.updateWindow()

class Terminal(QRunnable):
    chessWindow = None
    keepPlaying = None
    textDisplayed = None

    def __init__(self, window):
        super().__init__()
        self.chessWindow = window
        self.keepPlaying = True
        self.textDisplayed = False

    def run(self):
        self.runGame()

    def runGame(self):
        while self.keepPlaying is True:
            checkmate, draw = self.UUAIPlays()

            if checkmate:
                print("WHITE WINS")
                self.keepPlaying = False
            elif draw:
                print("IT IS A DRAW")
                self.keepPlaying = False


            if self.keepPlaying is True:
                checkmate, draw = self.StockfishPlays()
                if checkmate:
                    print("BLACK WINS")
                    self.keepPlaying = False
                elif draw:
                    print("IT IS A DRAW")
                    self.keepPlaying = False

    def UUAIPlays(self):
        # First we play(WHITE)
        legalMove = False

        while legalMove is False:
            try:
                playerInput = input()
                chessBoard.parse_san(playerInput)
                legalMove = True
            except:
                print("Illegal move try again")

        self.chessWindow.playMove(playerInput, "UUAI")
        return self.endOfGameCheck()

    def StockfishPlays(self):
        # Then the bot plays(BLACK)
        stockfish.set_position(stockfishMovesList)
        bestMove = stockfish.get_best_move()

        while chess.Move.from_uci(bestMove) in chessBoard.legal_moves is False:
            bestMove = stockfish.get_best_move()

        self.chessWindow.playMove(bestMove, "Stockfish")
        return self.endOfGameCheck()

    def endOfGameCheck(self):
        if chessBoard.is_checkmate():
            return True, False
        elif chessBoard.is_insufficient_material():
            return False, True
        else:
            return False, False

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
