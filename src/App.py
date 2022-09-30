import copy
import os
import random
import time
import numpy as np

from Config import *
from Record import Record
from AI import AI


def valid_input_case(board, currentPlayerNumber, last_play, prev_boards, line, column):
    """
    Vérifie si les données sont correctes selon les règles du jeu pour les cases

    Entrées :
        board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
        currentPlayerNumber [int] : numéro du joueur actuel
        last_play [{"line", "column", "direction"}] : dernier coup joué
        prev_boards [[board]] : liste des board précedement jouée
        line [int] : coordonnée de la ligne
        column [int] : coordonnée de la colonne

    Sorties :
        [bool] : données valides
    """

    valid = False

    valid_playable = board[line][column] != -1

    if valid_playable:

        valid_already_own = board[line][column] != currentPlayerNumber

        if valid_already_own:

            valid_last_play = not (
                line == last_play["line"] and column == last_play["column"])

            if valid_last_play or (last_play["line"] == None and last_play["column"] == None):

                nSize, nLine, nColumn = np.shape(prev_boards)

                valid = True
                prev = 0
                while valid and prev < nSize:

                    prev_equal = True
                    l = 0
                    while prev_equal and l < nLine:
                        c = 0
                        while prev_equal and c < nColumn:
                            if l == line and c == column:
                                prev_equal = prev_boards[prev][l][c] == currentPlayerNumber
                            else:
                                prev_equal = board[l][c] == prev_boards[prev][l][c]
                            c += 1
                        l += 1

                    valid = not prev_equal

                    prev += 1

    return valid


def valid_input_shift(board, currentPlayerNumber, last_play, prev_boards, line, direction):
    """
    Vérifie si les données sont correctes selon les règles du jeu pour les décallages

    Entrées :
        board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
        currentPlayerNumber [int] : numéro du joueur actuel
        last_play [{"line", "column", "direction"}] : dernier coup joué
        prev_boards [[board]] : liste des board précedement jouée
        line [int] : coordonnée de la ligne
        direction [+1 ou -1] : direction du décalage

    Sorties :
        [bool] : données valides
    """

    valid = False

    valid_format = direction in [+1, -1]

    if valid_format:

        if direction == +1:
            valid_edge = board[line][-1] == -1
        elif direction == -1:
            valid_edge = board[line][0] == -1

        if valid_edge:

            valid_last_play = not (
                line == last_play["line"] and (+1 if direction == -1 else -1) == last_play["direction"])

            if valid_last_play or (last_play["line"] == None and last_play["direction"] == None):

                nSize, nLine, nColumn = np.shape(prev_boards)

                valid = True
                prev = 0
                while valid and prev < nSize:

                    prev_equal = True
                    l = 0
                    while prev_equal and l < nLine:
                        c = 0
                        while prev_equal and c < nColumn:
                            if l == line:
                                prev_equal = board[l][c] == prev_boards[prev][l][0 if c +
                                                                                 direction == nColumn else c+direction]
                            else:
                                prev_equal = board[l][c] == prev_boards[prev][l][c]
                            c += 1
                        l += 1

                    valid = not prev_equal

                    prev += 1

    return valid


def playerWin(board):
    """
    Vérifie si un ou plusieurs joueur(s) à/ont gagné(s) la partie

    Entrées :
        board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau

    Sorties :
        [(bool, int)] : (égalité, numéro du joueur gagnant (ou None))
    """

    m_line = board
    m_column = np.rot90(board)
    m_diagonals = [np.diagonal(board, i) for i in range((-BOARD_SIZE+1)+NUMBER_CASE_TO_WIN-1,
                                                        (BOARD_SIZE+(BOARD_SIZE-1)*2)-NUMBER_CASE_TO_WIN+1)]  # Diagonnales de S-O vers N-E
    flipBoard = np.flipud(board)
    m_diagonals += [np.diagonal(flipBoard, i) for i in range((-BOARD_SIZE+1)+NUMBER_CASE_TO_WIN-1,
                                                             (BOARD_SIZE+(BOARD_SIZE-1)*2)-NUMBER_CASE_TO_WIN+1)]  # Diagonnales de N-O vers S-E

    for mat_elem in m_line:
        draw, winner = checkWin(mat_elem)
        if draw or winner != None:
            return (draw, winner)

    for mat_elem in m_column:
        draw, winner = checkWin(mat_elem)
        if draw or winner != None:
            return (draw, winner)

    for mat_elem in m_diagonals:
        draw, winner = checkWin(mat_elem)
        if draw or winner != None:
            return (draw, winner)

    return (False, None)


def checkWin(mat_elem):
    """
    Vérifie si un nombre (NUMBER_CASE_TO_WIN) de case du même joueur sont aligné

    Entrées :
        mat_elem [[]] : listes

    Sorties :
        [(bool, int)] : (égalité, numéro du joueur gagnant (ou None))
    """

    res = None
    draw = False

    n_find_1 = 0
    n_find_2 = 0

    if len(mat_elem) >= NUMBER_CASE_TO_WIN:

        for j in mat_elem:
            if j == 1:
                n_find_1 += 1
            else:
                n_find_1 = 0

            if j == 2:
                n_find_2 += 1
            else:
                n_find_2 = 0

            if n_find_1 == NUMBER_CASE_TO_WIN:
                if res == 2:
                    draw = True
                else:
                    res = 1
            elif n_find_2 == NUMBER_CASE_TO_WIN:
                if res == 1:
                    draw = True
                else:
                    res = 2

    return (draw, res)


def coup(board, line=None, column=None, playerNumber=None, direction=None):
    """
    Joue le coup sur la board

    Entrées :
        board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
        line [int] : coordonnée de la ligne
        column [int] : coordonnée de la colonne
        playerNumber [int] : numéro du joueur
        direction [+1 ou -1] : direction du décalage

    Sorties :
        [{"line", "column", "direction"}] : coup joué
    """

    if line != None and column != None and playerNumber != None:  # Coordonnées case

        board[line][column] = playerNumber

    elif line != None and direction != None:  # Décalage

        board[line] = np.roll(board[line], direction)

    return {"line": line, "column": column, "direction": direction}


class App():
    def __init__(self, pyqt):
        """
        Initialise les données de la partie

        Entrées :
            pyqt [pyqt] : class gérant le frontend
        """

        self.pyqt = pyqt
        self.record = Record(self)

        self.playerNames = ["", ""]
        self.score = [0, 0]
        self.playerMode = [1, 1]
        self.aiTimer = [0, 0]

        self.firstGame = True

        self.__init()

    def __init(self):
        """Définit les paramêtres d'une nouvelle manche"""

        ml = [-1 for x in range(BOARD_SIZE-1)]
        ca = [0 for l in range(BOARD_SIZE)]
        mr = [-1 for x in range(BOARD_SIZE-1)]

        self.board = np.array(
            [ml + ca + mr for l in range(BOARD_SIZE)], dtype=int)
        self.started = False
        self.currentPlayerNumber = 2
        self.last_play = {"line": None, "column": None, "direction": None}

        if not self.firstGame:
            self.record.newGame()
        else:
            self.firstGame = False

    def getBoard(self):
        """Donne le plateau"""

        return self.board

    def getValidCase(self):
        """Donne la liste des cases jouables"""

        playable_coups = []

        for l in range(BOARD_SIZE):
            for c in range(BOARD_SIZE+(BOARD_SIZE-1)*2):
                if valid_input_case(self.board, self.currentPlayerNumber, self.last_play, self.record.getCurrentBoard()[:-1], l, c):
                    playable_coups.append((l, c))

        return playable_coups

    def getValidShift(self, direction):
        """Donne la liste des décallages possibles"""

        playable_coups = []

        for l in range(BOARD_SIZE):
            if valid_input_shift(self.board, self.currentPlayerNumber, self.last_play, self.record.getCurrentBoard()[:-1], l, direction):
                playable_coups.append((l, direction))

        return playable_coups

    def getValid(self):
        valid = [(line, column, None)
                 for line, column in self.getValidCase()]
        valid += [(line, None, direction)
                  for line, direction in self.getValidShift(-1)]
        valid += [(line, None, direction)
                  for line, direction in self.getValidShift(+1)]

        return valid

    def nextPlayer(self):
        """Met à jour le joueur actuel et le fait jouer si c'est une ia"""

        if self.started:

            if self.currentPlayerNumber == 1:
                self.currentPlayerNumber = 2
            else:
                self.currentPlayerNumber = 1

            self.pyqt.initUI()

            if self.started and self.playerMode[self.currentPlayerNumber-1] in [-1, -2, -3]:

                self.playerAi()

    def playerAi(self):
        """Joue un coup en tant qu'ia"""

        startTime = time.time()
        input_line, input_column, input_direction = AI(self).play()
        endTime = time.time()
        delta = endTime - startTime
        if delta > AI_TIME:
            self.setScore((self.currentPlayerNumber % 2)+1)
            self.restart()
            self.setStarted(True)
            self.pyqt.initUI()
        else:
            waitTime = self.aiTimer[self.currentPlayerNumber-1]
            while delta < waitTime:
                delta = time.time() - startTime

            if input_line != None and input_column != None:
                self.setBoardCase(input_line, input_column)
            elif input_line != None and input_direction != None:
                self.setBoardShift(input_line, input_direction)

    def setCoup(self, board, line=None, column=None, playerNumber=None, direction=None):
        """Joue un coup sur la board"""

        pres = board[line][column] if line != None and column != None and playerNumber != None else None
        coup(board, line=line, column=column,
             playerNumber=playerNumber, direction=direction)
        return (self.board, pres)

    def setBoardCase(self, line, column):
        """
        Joue une case sur le plateau

        Entrées :
            user_input_line [int] : ligne
            user_input_column [int] : colonne
            relative [bool] : True si les données sont sous la forme A1 ou 1+
        """

        self.last_play = coup(
            self.board, line=line, column=column, playerNumber=self.currentPlayerNumber)

        self.record.addBoard(self.board)

        self.nextPlayer()

    def setBoardShift(self, line, direction):
        """
        Joue un décalage sur le plateau

        Entrées :
            user_input_direction [+1 ou -1] : +1 à droite et -1 à gauche
            user_input_line [int] : ligne

        Sorties :
        """

        self.last_play = coup(self.board, line=line, direction=direction)

        self.record.addBoard(copy.deepcopy(self.board))

        self.nextPlayer()

    def getCurrentPlayer(self):
        """Donne le joueur actuel"""

        return self.currentPlayerNumber

    def getPlayerMode(self, playerNumber=None):
        """
        Donne le mode du joueur

        Entrées :
            playerNumber [int] : numéro du joueur
        """

        return self.playerMode[self.currentPlayerNumber-1] if playerNumber == None else self.playerMode[playerNumber-1]

    def setPlayerMode(self, playerNumber, mode):
        """
        Modifie le mode du joueur

        Entrées :
            playerNumber [int] : numéro du joueur
            mode [+1 ou -1] : +1 pour humain et -1 pour ia
        """

        self.playerMode[playerNumber-1] = mode

    def getAiTimer(self, playerNumber):
        """
        Donne le temps d'exécution de l'ia

        Entrées :
            playerNumber [int] : numéro du joueur
        """

        return self.aiTimer[playerNumber-1]

    def setAiTimer(self, playerNumber, timer):
        """
        Modifie le temps d'exécution de l'ia

        Entrées :
            playerNumber [int] : numéro du joueur
            timer [int] : temps d'exécution de l'ia
        """

        self.aiTimer[playerNumber-1] = timer

    def getWinner(self, board=None):
        """Donne le gagnant(s) de la partie ou None"""

        return playerWin(self.board if board is None else board)

    def getStarted(self):
        """Donne l'état de la partie"""

        return self.started

    def setStarted(self, boolVal):
        """
        Modifie l'état de la partie

        Entrées :
            boolVal [int] : démarrer ou arrêter ?
        """

        if boolVal == False:
            self.started = boolVal
        else:
            self.started = boolVal
            self.nextPlayer()

    def restart(self):
        """Redémare une partie"""

        self.__init()

    def getPlayerName(self, playerNumber=None):
        """
        Donne le nom du joueur en fonction de son numéro

        Entrées :
            playerNumber [int] : numéro du joueur
        """

        return self.playerNames if playerNumber == None else self.playerNames[playerNumber-1]

    def setPlayerName(self, playerNumber, playerName):
        """
        Donne le nom du joueur en fonction de son numéro

        Entrées :
            playerNumber [int] : numéro du joueur
            playerName [str] : nom du joueur
        """

        self.playerNames[playerNumber-1] = playerName

    def getScore(self, playerNumber):
        """
        Donne le score du joueur en fonction de son numéro

        Entrées :
            playerNumber [int] : numéro du joueur
        """

        return self.score[playerNumber-1]

    def setScore(self, playerNumber):
        """
        Rajoute un point au joueur

        Entrées :
            playerNumber [int] : numéro du joueur
        """

        self.score[playerNumber-1] += 1
