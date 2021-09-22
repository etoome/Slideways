import sys

from PyQt5.Qt import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDialog, QGridLayout, QGroupBox,
                             QHBoxLayout, QLabel, QLayout, QMainWindow,
                             QMessageBox, QPushButton, QSizePolicy, QSlider,
                             QVBoxLayout, QWidget)


class appIcon(QPushButton):
    def __init__(self):
        """Icon de l'application"""

        super().__init__()

        self.setIconSize(QSize(100, 100))
        self.setIcon(QIcon('./images/icon.png'))
        self.setStyleSheet('border:none;')
        self.setFocusPolicy(Qt.NoFocus)


class startGame(QPushButton):
    def __init__(self):
        """Bouton de validation des noms de joueurs"""

        super().__init__()

        self.setIconSize(QSize(40, 40))
        self.setIcon(QIcon('./images/check.png'))
        self.setStyleSheet('border:none;')


class hardcoreButton(QPushButton):
    def __init__(self):
        """CheckBox du mode hardcore"""

        super().__init__()

        self.setFixedSize(40, 40)
        self.setIconSize(QSize(30, 30))
        self.setToolTip('Hardcore Mode (You have to win the game)')
        self.setStyleSheet("QPushButton{ border:none; }")
        self.checked = False
        self.__updateIcon()

        self.clicked.connect(lambda: self.changeState())

    def __updateIcon(self):
        """Met à jour l'icon"""

        if self.checked:
            self.setIcon(QIcon('./images/hardcore_on.png'))
        else:
            self.setIcon(QIcon('./images/hardcore_off.png'))

    def changeState(self):
        """Change l'état"""

        self.checked = not self.checked
        self.__updateIcon()

    def isChecked(self):
        """Donne l'état"""

        return self.checked


class recordButton(QPushButton):
    def __init__(self):
        """CheckBox pour l'enregistrement"""

        super().__init__()

        self.setFixedSize(40, 40)
        self.setIconSize(QSize(20, 20))
        self.setToolTip('Record this game')
        self.setStyleSheet("QPushButton{ border:none; }")
        self.checked = False
        self.__updateIcon()

        self.clicked.connect(lambda: self.changeState())

    def __updateIcon(self):
        """Met à jour l'icon"""

        if self.checked:
            self.setIcon(QIcon('./images/record_on.png'))
        else:
            self.setIcon(QIcon('./images/record_off.png'))

    def changeState(self):
        """Change l'état"""

        self.checked = not self.checked
        self.__updateIcon()

    def isChecked(self):
        """Donne l'état"""

        return self.checked

class replayButton(QPushButton):
    def __init__(self):
        """Bouton pour charger un replay"""

        super().__init__()

        self.setFixedSize(40, 40)
        self.setIconSize(QSize(30, 30))
        self.setIcon(QIcon('./images/replay.png'))
        self.setToolTip('Replay a game')
        self.setStyleSheet("QPushButton{ border:none; }")


class playerButton(QPushButton):
    def __init__(self, playerNumber, toPlay):
        """
        Bouton permetant de changer le joueur de mode (ia ou humain)

        Entrées :
            playerNumber [int] : numéro de joueur
            toPlay [bool] : est-ce à lui de jouer ?
        """

        super().__init__()

        self.setFixedSize(80, 80)
        self.setIconSize(QSize(60, 60))

        styleSheet = "border-radius: 8px;"

        if toPlay:
            styleSheet += "border: 5px solid black;"
        else:
            styleSheet += "border: 3px solid black;"

        if playerNumber == 1:
            styleSheet += "background-color:#E22327;"
        elif playerNumber == 2:
            styleSheet += "background-color:#F8EE48;"

        self.setStyleSheet("QPushButton{"+styleSheet+"}")

    def getMode(self):
        """Donne le mode du joueur"""

        return self.mode

    def setHuman(self):
        """Modifie le mode du joueur vers humain"""

        self.mode = 1
        self.setIcon(QIcon('./images/human.png'))

    def setAI(self, mode):
        """Modifie le mode du joueur vers ia"""

        self.mode = mode
        if mode == -1:
            self.setIcon(QIcon('./images/ai_easy.png'))
        elif mode == -2:
            self.setIcon(QIcon('./images/ai_medium.png'))
        elif mode == -3:
            self.setIcon(QIcon('./images/ai_hard.png'))


    def setClickable(self, val):
        """Active ou désactive le bouton"""

        self.setEnabled(val)
        self.setToolTip('Click to change mode.' if val else '')


class startButton(QPushButton):
    def __init__(self, started):
        """
        Boutton de start ou de restart

        Entrées :
            started [bool] : est-ce que la partie est en cours ?
        """

        super().__init__()

        self.setFixedSize(60, 60)
        self.setIconSize(QSize(40, 40))
        self.setStyleSheet('border:none;')

        if started == True:
            self.setIcon(QIcon('./images/restart.png'))
        else:
            self.setIcon(QIcon('./images/start.png'))


class playerName(QLabel):
    def __init__(self, playerNumber, playerName, timer=None):
        """
        Le nom du joueur avec son temps d'exécution si c'est une ia

        Entrées :
            playerNumber [int] : numéro de joueur
            playerName [str] : nom du joueur
        """

        super().__init__()

        self.setText(playerName + (' - {}s'.format(timer)
                                   if timer != None else ''))
        self.setAlignment(Qt.AlignLeft if playerNumber == 1 else Qt.AlignRight)
        self.setStyleSheet("font : 12pt;")
        self.setFocusPolicy(Qt.NoFocus)


class aiSlider(QSlider):
    def __init__(self):
        """Un slider pour le temps d'éxecution de l'ia"""

        super().__init__(Qt.Horizontal)

        self.setEnabled(False)
        self.setRange(0, 10)
        self.setTickInterval(1)
        self.setSingleStep(1)
        self.setPageStep(1)
        self.setTickPosition(QSlider.TicksBelow)


class moveLineButton(QPushButton):
    def __init__(self, line, direction):
        """
        Boutton pour déplacer les lignes

        Entrées :
            direction [+1 ou -1] : +1 vers la droite et -1 vers la gauche
            line [int] : ligne
        """

        super().__init__()

        self.direction = direction
        self.line = line

        self.setFixedSize(50, 50)
        self.setIconSize(QSize(20, 20))
        self.setStyleSheet("border: none;")

        if direction == +1:
            self.setIcon(QIcon('./images/right.png'))
        elif direction == -1:
            self.setIcon(QIcon('./images/left.png'))

    def getDirection(self):
        """Donne la direction"""

        return self.direction

    def getLine(self):
        """Donne la ligne"""

        return self.line


class gridButton(QPushButton):
    def __init__(self, line, column, owner, enabled):
        """
        Case du plateau

        Entrées :
            line [int] : ligne 
            column [int] : colonne
            owner [0, 1 ou 2] : numéro du joueur à qui appartient la case (0 pour aucun)
            enabled [bool] : est-ce que le coup est jouable ?
        """

        super().__init__()

        self.owner = owner
        self.setEnabled(enabled)
        self.setFixedSize(50, 50)

        if self.owner == -1:
            self.setStyleSheet("border:none;")
        elif self.owner == 0:
            if self.isEnabled():
                self.setStyleSheet(
                    "border: 5px solid #306CDC; background-color: rgb(55, 114, 214);")
            else:
                self.setStyleSheet(
                    "border: 5px solid #306CDC; background-color: rgb(25, 84, 184);")
        elif self.owner == 1:
            if self.isEnabled():
                self.setStyleSheet(
                    "border: 5px solid #306CDC; background-color: rgb(226, 35, 39);")
            else:
                self.setStyleSheet(
                    "border: 5px solid #306CDC; background-color: rgb(196, 5, 9);")
        elif self.owner == 2:
            if self.isEnabled():
                self.setStyleSheet(
                    "border: 5px solid #306CDC; background-color: rgb(248, 238, 72);")
            else:
                self.setStyleSheet(
                    "border: 5px solid #306CDC; background-color: rgb(218, 208, 42);")


class playerSquare(QPushButton):
    def __init__(self, playerNumber, playerMode, toPlay=False):
        """
        Affiche le joueur avec son mode

        Entrées :
            playerNumber [int] : numéro du joueur
            playerMode [-1 ou +1] : -1 pour ia et +1 pour humain
        """

        super().__init__()

        self.setFixedSize(80, 80)
        self.setIconSize(QSize(60, 60))
        self.setFocusPolicy(Qt.NoFocus)

        if playerMode == -1:
            self.setIcon(QIcon('./images/ai_easy.png'))
        elif playerMode == -2:
            self.setIcon(QIcon('./images/ai_medium.png'))
        elif playerMode == -3:
            self.setIcon(QIcon('./images/ai_hard.png'))
        else:
            self.setIcon(QIcon('./images/human.png'))

        styleSheet = ""

        if toPlay:
            styleSheet += "border: 5px solid black;"
        else:
            styleSheet += "border: 3px solid black;"

        if playerNumber == 1:
            styleSheet += "border-radius: 8px;background-color:#E22327;"
        elif playerNumber == 2:
             styleSheet += "border-radius: 8px;background-color:#F8EE48;"

        self.setStyleSheet(styleSheet)


class winnerName(QLabel):
    def __init__(self, draw, playerName=""):
        """
        Affiche le message de victoire

        Entrées :
            draw [bool] : égalité ?
            playerName [str] : nom du joueur
        """

        super().__init__()

        if draw:
            self.setText('draw !')
        else:
            self.setText('{} win !'.format(playerName))

        self.setStyleSheet("font : 15pt;")
        self.setFixedHeight(100)
        self.setFocusPolicy(Qt.NoFocus)

class closeButton(QPushButton):
    def __init__(self):
        """Bouton de fermeture"""

        super().__init__()

        self.setFixedSize(60, 60)
        self.setIconSize(QSize(40, 40))
        self.setStyleSheet('border:none;')
        self.setIcon(QIcon('./images/close.png'))



class scoreLabel(QLabel):
    def __init__(self, score):
        """
        Affiche le nombre de point(s)

        Entrées :
            score [int] : score du joueur
        """

        super().__init__()

        self.setText("I"*score if score > 0 else "")
        self.setStyleSheet("font : 15pt;")
        self.setFixedHeight(25)
        self.setFocusPolicy(Qt.NoFocus)
