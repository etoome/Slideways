import numpy as np

from PyQt5 import QtCore
from PyQt5.Qt import QSize, Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import (QApplication, QGridLayout,
                             QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow,
                             QVBoxLayout, QWidget, QFileDialog)

from App import App
from Replay import Replay
from Components import *


class Window(QMainWindow):
    def __init__(self):
        """Initialise la fenêtre"""

        super().__init__()
        self.title = 'Slideways'
        self.app = App(self)
        self.firstStart = True
        self.replay = None
        self.initUI()

        self.__hardcore = False

    def closeEvent(self, event):
        """Est appelée lorsque l'utilisateur ferme la fenêtre"""

        if self.__hardcore:
            QMessageBox.critical(
                self, 'Nice try !', "Hardcore mode activated !\nYou have to beat me...", QMessageBox.Ok)
            event.ignore()
        else:
            if self.app.record.isRecording():
                self.app.record.close()
            event.accept()

    def keyPressEvent(self, event):
        """Est appelée lorsqu'une touche est pressée"""

        if event.key() == Qt.Key_Right:
            if self.replay != None:
                self.replay.next()
                self.initUI()
        elif event.key() == Qt.Key_Left:
            if self.replay != None:
                self.replay.previous()
                self.initUI()

        event.accept()

    def __setHardcore(self, boolVal):
        """
        Active ou désactive le mode hardcore

        Entrées :
            boolVal [bool] : valeur à modifier
        """

        if boolVal:
            self.__hardcore = True
            self.__hardcoreLoop()
        else:
            self.__hardcore = False

    def __hardcoreLoop(self):
        """Empeche l'utilisateur de cliquer sur la croix pour fermer la fenêtre"""

        if self.__hardcore:
            cursorPos = QCursor().pos()
            x = cursorPos.x()
            y = cursorPos.y()

            wx = self.x()
            wy = self.y()
            width = self.width()
            height = self.height()

            if wx + width - 60 < x < wx + width + 60 and wy - 50 < y < wy + 50:
                self.setGeometry(x, y, width, height)

            QTimer().singleShot(100, lambda: self.__hardcoreLoop())

    def initUI(self):
        """Initialise le layout global"""

        self.setWindowTitle(
            self.title + (' - 🔴 Recording...' if self.app.record.isRecording() else ''))
        self.setWindowIcon(QIcon('./images/icon.png'))

        if self.firstStart:
            windowLayout = self.startLayout()
        elif self.replay != None:
            windowLayout = self.replayLayout()
        else:

            draw, winner = self.app.getWinner()

            if draw or winner != None:
                self.statusBar().clearMessage()

                if draw:
                    self.app.setScore(1)
                    self.app.setScore(2)
                    winner = 0
                else:
                    self.app.setScore(winner)

                self.app.setStarted(False)
                windowLayout = self.winLayout(winner)

            else:
                self.statusBar().showMessage('Tip : Click on player icon to change mode.')

                windowLayout = QGridLayout()
                windowLayout.addLayout(self.scoreLayout(), 0, 0, 1, 0)
                windowLayout.addLayout(self.topLayout(), 1, 0, 1, 0)
                windowLayout.addLayout(
                    self.moveLinesLayout(-1, clickable=self.app.getStarted() and self.app.getPlayerMode() == 1), 2, 0)
                windowLayout.addLayout(self.boardLayout(self.app.getBoard(
                ), clickable=self.app.getStarted() and self.app.getPlayerMode() == 1), 2, 1)
                windowLayout.addLayout(
                    self.moveLinesLayout(+1, clickable=self.app.getStarted() and self.app.getPlayerMode() == 1), 2, 2)

        mainWidget = QWidget()
        mainWidget.setLayout(windowLayout)
        self.setCentralWidget(mainWidget)

        self.show()

        # Force la fenêtre à prendre la taille la plus petite
        for i in range(0, 10):
            QApplication.processEvents()
        self.resize(self.minimumSizeHint())

    def startLayout(self):
        """Layout de démarage. Demande le nom de chaque joueur"""

        sLayout = QGridLayout()
        sLayout.setContentsMargins(80, 50, 80, 50)
        sLayout.setSpacing(5)
        sLayout.setAlignment(Qt.AlignCenter)

        iconImage = appIcon()
        iconImage.setFixedSize(QSize(200, 200))

        np1 = QLabel("Player 1 :")
        np1.setStyleSheet('font:12pt;')
        textbox1 = QLineEdit()
        textbox1.setText('🌝')
        textbox1.setStyleSheet('font:12pt;border: 3px solid #E22327;')

        np2 = QLabel("Player 2 :")
        np2.setStyleSheet('font:12pt;')
        textbox2 = QLineEdit()
        textbox2.setText('🌚')
        textbox2.setStyleSheet('font:12pt;border: 3px solid #F8EE48;')

        btStart = startGame()
        btStart.setFixedSize(QSize(100, 100))

        optionsLayout = QGridLayout()
        bHardcore = hardcoreButton()
        bRecord = recordButton()
        bReplay = replayButton()
        optionsLayout.addWidget(bHardcore, 0, 0)
        optionsLayout.addWidget(bRecord, 0, 1)
        optionsLayout.addWidget(bReplay, 0, 2)

        bReplay.clicked.connect(self.__setReplay)

        btStart.clicked.connect(lambda x, y=textbox1,
                                z=textbox2, h=bHardcore, r=bRecord: self.__setPlayerNames(y, z, h.isChecked(), r.isChecked()))

        sLayout.addWidget(iconImage, 0, 0, alignment=Qt.AlignCenter)
        sLayout.addWidget(np1, 1, 0)
        sLayout.addWidget(textbox1, 2, 0)
        sLayout.addWidget(np2, 3, 0)
        sLayout.addWidget(textbox2, 4, 0)
        sLayout.addWidget(btStart, 5, 0, alignment=Qt.AlignCenter)
        sLayout.addLayout(optionsLayout, 6, 0, alignment=Qt.AlignCenter)

        return sLayout

    def __setPlayerNames(self, tb1, tb2, hardcore, record):
        """
        Met à jour les noms des joueurs

        Entrées :
            tb1 [QLineEdit] : textbox1
            tb2 [QLineEdit] : textbox2
            hardcore [bool] : mode hardcore ?
            record [bool] : record ?
        """

        self.firstStart = False

        tb1Txt = tb1.text()
        tb2Txt = tb2.text()

        if tb1Txt != tb2Txt and tb1Txt.strip() != "" and tb2Txt.strip() != "":
            self.app.setPlayerName(1, tb1Txt)
            self.app.setPlayerName(2, tb2Txt)

        self.__setHardcore(hardcore)

        if record:
            self.app.record.startRecord()

        self.initUI()

    def scoreLayout(self):
        """Layout des scores des joueurs"""

        sLayout = QHBoxLayout()

        sl1 = scoreLabel(self.app.getScore(1))
        sl2 = scoreLabel(self.app.getScore(2))
        sLayout.addWidget(sl1, alignment=Qt.AlignLeft)
        sLayout.addWidget(sl2, alignment=Qt.AlignRight)

        return sLayout

    def topLayout(self):
        """Layout de l'entête"""

        tLayout = QHBoxLayout()
        tLayout.setSpacing(50)

        # Layout de gauche
        pb1 = playerButton(1, None if not self.app.getStarted()
                           else self.app.getCurrentPlayer() == 1)
        aiSliderWidget1 = aiSlider()
        aiSliderWidget1.setValue(self.app.getAiTimer(1))
        nameSliderLayout1 = QVBoxLayout()
        nameSliderLayout1.setContentsMargins(5, 20, 5, 20)

        if self.app.getPlayerMode(1) in [-1, -2, -3]:
            aiSliderWidget1.setEnabled(True)
            pb1.setAI(self.app.getPlayerMode(1))
            nameSliderLayout1.addWidget(
                playerName(1, self.app.getPlayerName(1), timer=aiSliderWidget1.value()))
        else:
            aiSliderWidget1.setEnabled(False)
            pb1.setHuman()
            nameSliderLayout1.addWidget(
                playerName(1, self.app.getPlayerName(1)))

        nameSliderLayout1.addWidget(aiSliderWidget1)

        # Evenements du layout de gauche
        pb1.clicked.connect(
            lambda x, y=pb1, z=aiSliderWidget1: self.__updatePlayerMode(1, y, z))
        aiSliderWidget1.valueChanged.connect(lambda val: (
            self.app.setAiTimer(1, val), self.initUI()))

        # Layout du centre
        sb = startButton(self.app.getStarted())
        sb.clicked.connect(lambda x: (self.app.restart() if self.app.getStarted(
        ) else None, self.app.setStarted(True), self.initUI()))

        # Layout de droite
        pb2 = playerButton(2, None if not self.app.getStarted()
                           else self.app.getCurrentPlayer() == 2)
        aiSliderWidget2 = aiSlider()
        aiSliderWidget2.setValue(self.app.getAiTimer(2))
        nameSliderLayout2 = QVBoxLayout()
        nameSliderLayout2.setContentsMargins(5, 20, 5, 20)

        if self.app.getPlayerMode(2) in [-1, -2, -3]:
            aiSliderWidget2.setEnabled(True)
            pb2.setAI(self.app.getPlayerMode(2))
            nameSliderLayout2.addWidget(
                playerName(2, self.app.getPlayerName(2), timer=aiSliderWidget2.value()))
        else:
            aiSliderWidget2.setEnabled(False)
            pb2.setHuman()
            nameSliderLayout2.addWidget(
                playerName(2, self.app.getPlayerName(2)))

        nameSliderLayout2.addWidget(aiSliderWidget2)

        # Evenements du layout de droite
        pb2.clicked.connect(
            lambda x, y=pb2, z=aiSliderWidget2: self.__updatePlayerMode(2, y, z))
        aiSliderWidget2.valueChanged.connect(
            lambda val: (self.app.setAiTimer(2, val), self.initUI()))

        # Fixe les paramêtres lors du débuts de la partie
        if not self.app.getStarted():
            pb1.setClickable(True)
            pb2.setClickable(True)
        else:
            pb1.setClickable(False)
            pb2.setClickable(False)

        # Mode Hardcore
        if self.__hardcore:
            pb1.setClickable(False)
            self.app.setPlayerMode(2, -3)
            pb2.setAI(-3)
            pb2.setClickable(False)

        # Met à jour le layout global
        tLayout.addWidget(pb1)
        tLayout.addLayout(nameSliderLayout1)
        tLayout.addWidget(sb)
        tLayout.addLayout(nameSliderLayout2)
        tLayout.addWidget(pb2)

        return tLayout

    def __updatePlayerMode(self, playerNumber, pb, aiSliderWidget):
        """
        Met à jour le mode du joueur

        Entrées :
            playerNumber [int] : numéro du joueur
            pb [playerButton] : boutton du joueur
            aiSliderWidget [aiSlider] : slider pour le temps d'exécution de l'ia
        """

        if pb.getMode() == 1:
            aiSliderWidget.setEnabled(True)
            self.app.setPlayerMode(playerNumber, -1)
        elif pb.getMode() == -1:
            aiSliderWidget.setEnabled(True)
            self.app.setPlayerMode(playerNumber, -2)
        elif pb.getMode() == -2:
            aiSliderWidget.setEnabled(True)
            self.app.setPlayerMode(playerNumber, -3)
        else:
            aiSliderWidget.setEnabled(False)
            self.app.setPlayerMode(playerNumber, 1)

        self.initUI()

    def boardLayout(self, board, clickable=True):
        """
        Layout du plateau

        Entrées :
            board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
            clickable [bool] : case clickable ?
        """

        bLayout = QGridLayout()

        if clickable:
            playableCase = self.app.getValidCase()

        for line in range(len(board)):
            for column in range(len(board[0])):

                btPlayable = (
                    line, column) in playableCase if clickable else True

                gb = gridButton(line, column, board[line][column], btPlayable)

                bLayout.addWidget(gb, line, column)

                if clickable and btPlayable:
                    gb.clicked.connect(
                        lambda x, l=line, c=column: self.app.setBoardCase(l, c))
                else:
                    gb.setFocusPolicy(Qt.NoFocus)

        return bLayout

    def moveLinesLayout(self, direction, clickable=True):
        """
        Layout du déplacement des lignes

        Entrées :
            direction [int] : +1 à droite et -1 à gauche
            clickable [bool] : case clickable ?
        """

        mlLayout = QGridLayout()

        if clickable:
            validShift = self.app.getValidShift(direction)

        for line in range(len(self.app.getBoard())):
            mlb = moveLineButton(line, direction)

            if clickable and (line, direction) in validShift:
                mlb.setEnabled(True)
            else:
                mlb.setEnabled(False)

            if clickable:
                mlb.clicked.connect(lambda x, y=mlb: self.app.setBoardShift(
                    y.getLine(), y.getDirection()))
            mlLayout.addWidget(mlb, line, 0)

        return mlLayout

    def winLayout(self, winner):
        """
        Layout en cas de victoire

        Entrées :
            winner [int] : numéro du gagnant ou 0 si égalité
        """

        wLayout = QGridLayout()
        wLayout.setContentsMargins(50, 50, 50, 20)

        wpLayout = QHBoxLayout()
        if winner == 0:  # Egalité
            wp1 = playerSquare(1, self.app.getPlayerMode(1))
            wp1.setFixedSize(100, 100)
            wpLayout.addWidget(wp1)

            wp2 = playerSquare(2, self.app.getPlayerMode(2))
            wp2.setFixedSize(100, 100)
            wpLayout.addWidget(wp2)

            wn = winnerName(True)
        else:
            wp1 = playerSquare(winner, self.app.getPlayerMode(winner))
            wp1.setFixedSize(100, 100)
            wpLayout.addWidget(wp1)

            wn = winnerName(False, self.app.getPlayerName(winner))

        scLayout = QGridLayout()
        sb = startButton(True)
        sb.clicked.connect(lambda x: (self.app.restart(),
                           self.app.setStarted(True), self.initUI()))
        cb = closeButton()
        cb.clicked.connect(lambda x: (self.app.record.close(
        ) if self.app.record.isRecording() else None, self.close()))
        scLayout.addWidget(sb, 0, 0)
        scLayout.addWidget(cb, 0, 1)

        wLayout.addLayout(wpLayout, 0, 0, alignment=Qt.AlignCenter)
        wLayout.addWidget(wn, 1, 0, alignment=Qt.AlignCenter)
        wLayout.addLayout(self.boardLayout(
            self.app.getBoard(), clickable=False), 2, 0, alignment=Qt.AlignCenter)
        wLayout.addLayout(scLayout, 3, 0, alignment=Qt.AlignCenter)

        # Désactive la mode Hardcore si le joueur 1 gagne ou fait égalité
        if self.__hardcore and winner in [0, 1]:
            self.__hardcore = False
            hLabel = QLabel('Hardcore Mode disabled !')
            wLayout.addWidget(hLabel, 4, 0, alignment=Qt.AlignCenter)

        return wLayout

    def replayLayout(self):
        """Layout du Replay"""

        rLayout = QGridLayout()
        rLayout.setContentsMargins(50, 50, 50, 50)

        cpn = self.replay.getCurrentPlayerNumber()
        ps1 = playerSquare(1, self.replay.getPlayerMode(1), cpn == 1)
        ps2 = playerSquare(2, self.replay.getPlayerMode(2), cpn == 2)
        ml1 = moveLineButton(None, -1)
        ml1.setFixedSize(80, 80)
        ml1.setIconSize(QSize(50, 50))
        ml1.setFocusPolicy(Qt.NoFocus)
        if not self.replay.hasPrevious():
            ml1.setEnabled(False)
        ml2 = moveLineButton(None, +1)
        ml2.setFixedSize(80, 80)
        ml2.setIconSize(QSize(50, 50))
        ml2.setFocusPolicy(Qt.NoFocus)
        if not self.replay.hasNext():
            ml2.setEnabled(False)

        ml1.clicked.connect(lambda x: (self.replay.previous(), self.initUI()))
        ml2.clicked.connect(lambda x: (self.replay.next(), self.initUI()))

        draw, winner = self.replay.getWinner()

        if draw or winner != None:
            ps = playerSquare(winner, self.replay.getPlayerMode(winner))
            ps.setFixedSize(100, 100)
            wn = winnerName(draw, self.replay.getPlayerName(winner))

            rLayout.addWidget(ps, 0, 1, alignment=Qt.AlignCenter)
            rLayout.addWidget(wn, 1, 1, alignment=Qt.AlignCenter)
        else:
            sl1 = scoreLabel(self.replay.getScore(1))
            sl2 = scoreLabel(self.replay.getScore(2))
            pn1 = playerName(1, self.replay.getPlayerName(1))
            pn2 = playerName(2, self.replay.getPlayerName(2))
            vs = QLabel('VS')
            vs.setStyleSheet('font:20pt;')

            rLayout.addWidget(sl1, 0, 0, alignment=Qt.AlignLeft)
            rLayout.addWidget(sl2, 0, 2, alignment=Qt.AlignRight)

            pspnLayout = QGridLayout()
            pspnLayout.addWidget(ps1, 0, 0, alignment=Qt.AlignCenter)

            pspnLayout.addWidget(pn1, 0, 1, alignment=Qt.AlignCenter)
            pspnLayout.addWidget(vs, 0, 2, alignment=Qt.AlignCenter)
            pspnLayout.addWidget(pn2, 0, 3, alignment=Qt.AlignCenter)

            pspnLayout.addWidget(ps2, 0, 4, alignment=Qt.AlignCenter)

            rLayout.addLayout(pspnLayout, 1, 1)

        rLayout.addWidget(ml1, 2, 0, alignment=Qt.AlignCenter)
        rLayout.addLayout(self.boardLayout(
            self.replay.getBoard(), clickable=False), 2, 1, alignment=Qt.AlignCenter)
        rLayout.addWidget(ml2, 2, 2, alignment=Qt.AlignCenter)

        return rLayout

    def __setReplay(self):
        """Charge un enregistrement"""

        filePath = QFileDialog.getOpenFileName(
            self, 'Choose a file', './Replay', "*.slideways")[0]
        if filePath != '':
            self.firstStart = False

            try:
                self.replay = Replay(filePath)
            except Exception as e:
                errorBox(e)

        self.initUI()


def errorBox(e):
    """MessageBox en cas d'erreur"""

    errorBox = QMessageBox()
    errorBox.setWindowTitle('Error')
    errorBox.setText('Something bad happend !')
    errorBox.setDetailedText(str(e))
    errorBox.setStandardButtons(QMessageBox.Close)
    errorBox.setIcon(QMessageBox.Critical)
    errorBox.exec_()

    sys.exit()
