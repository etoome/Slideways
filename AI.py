import random
import copy
import time
import numpy as np

from Config import *


def coup_AI(plateau, playerNumber, line=None, column=None, direction=None):
    """
    Simule le coup d'un joueur sur un plateau

    Entrées :
        plateau [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
        playerNumber [int] : numéro du joueur
        line [int] : coordonnée de la ligne
        column [int] : coordonnée de la colonne
        direction [+1 ou -1] : direction du décalage
    """

    board = copy.deepcopy(plateau)

    if line != None and column != None:  # Coordonnées case

        board[line][column] = playerNumber

    elif line != None and direction != None:  # Décalage

        board[line] = np.roll(board[line], direction)

    return board


class AI():
    def __init__(self, app):
        """Initialise l'IA basé sur app"""

        self.app = app
        self.mode = self.app.getPlayerMode()

    def play(self):
        """
        Jouer le coup en tant qu'ia

        Sorties :
            [(line, column, direction)] : tuple du coup
        """

        if self.mode == -1:
            return self.alphaBeta(self.app.getBoard(), self.app.getCurrentPlayer())[0]
        elif self.mode == -2:
            self.heuristique = self.heuristique_max
            return self.alphaBetaHeuristique(self.app.getBoard(), self.app.getCurrentPlayer())[0]
        elif self.mode == -3:
            self.heuristique = self.heuristique_mean
            return self.alphaBetaHeuristique(self.app.getBoard(), self.app.getCurrentPlayer())[0]

    def alphaBeta(self, board, player, depth=2, maxi=True):
        """
        IA AlphaBeta

        Entrées :
            board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
            player [int] : numéro du joueur
            depth [int] : profondeur d'itération
            maxi [bool] : maximise le joueur actuel

        Sorties :
            [(score, (line, column, direction))] : la meilleur coup avec son score
        """

        otherPlayer = (player % 2)+1

        if depth == 0:
            AI_tie, AI_win_player = self.app.getWinner(board)
            if AI_win_player == player:
                res = WIN
            elif AI_win_player == otherPlayer:
                res = LOSS
            else:
                res = DRAW

            return (None, res)

        meilleurscore = -INFINITE if maxi else +INFINITE
        meilleurcoup = []

        caseCoup = [(line, column, None)
                    for line, column in self.app.getValidCase()]
        shiftCoup = [(line, None, direction)
                     for line, direction in self.app.getValidShift(-1)]
        shiftCoup += [(line, None, direction)
                      for line, direction in self.app.getValidShift(+1)]

        for coup in caseCoup + shiftCoup:
            board, pres = self.app.setCoup(board, line=coup[0],
                                           column=coup[1], playerNumber=player, direction=coup[2])

            score = self.alphaBeta(
                board, otherPlayer, depth=depth-1, maxi=not maxi)[1]

            board, pres = self.app.setCoup(board, line=coup[0],
                                           column=coup[1], playerNumber=pres, direction=(+1 if coup[2] == -1 else -1))

            if (maxi and score > meilleurscore) or (not maxi and score < meilleurscore):
                meilleurscore = score
                meilleurcoup = [(coup, score)]
            elif meilleurscore == score:
                meilleurcoup.append((coup, score))
            else:
                break

        return random.choice(meilleurcoup)

    def alphaBetaHeuristique(self, board, playerNumber, depth=2, maxi=True):
        """
        IA AlphaBeta avec une fonction heuristique

        Entrées :
            board [[int,int,...],[int,int,...],...] : listes de listes représentant le plateau
            player [int] : numéro du joueur
            depth [int] : profondeur d'itération
            maxi [bool] : maximise le joueur actuel

        Sorties :
            [(score, (line, column, direction))] : la meilleur coup avec son score
        """

        otherPlayer = (playerNumber % 2)+1

        if depth == 0:
            return (None, self.heuristique(board, playerNumber if maxi else otherPlayer))

        meilleurscore = -INFINITE if maxi else +INFINITE
        meilleurcoup = []

        valid = self.app.getValid()

        for coup in valid:
            board, pres = self.app.setCoup(board, line=coup[0],
                                           column=coup[1], playerNumber=playerNumber, direction=coup[2])

            score = self.alphaBetaHeuristique(
                board, otherPlayer, depth=depth-1, maxi=not maxi)[1]

            board, pres = self.app.setCoup(board, line=coup[0],
                                           column=coup[1], playerNumber=pres, direction=(+1 if coup[2] == -1 else -1))

            if (maxi and score > meilleurscore) or (not maxi and score < meilleurscore):
                meilleurscore = score
                meilleurcoup = [(coup, score)]
            elif meilleurscore == score:
                meilleurcoup.append((coup, score))
            else:
                break

        return random.choice(meilleurcoup)

    def heuristique_max(self, board, playerNumber):
        """Evalue la probabilité que le player a de gagner sur cette board"""

        otherPlayer = (playerNumber % 2)+1

        # case du joueur par colonne
        ccp = np.count_nonzero(board == playerNumber, axis=0)
        ccpMax = np.amax(ccp)/NUMBER_CASE_TO_WIN

        # case du joueur par ligne
        clp = np.count_nonzero(board == playerNumber, axis=1)
        clpMax = np.amax(clp)/NUMBER_CASE_TO_WIN

        # case de l'autre joueur par colonne
        cco = np.count_nonzero(board == otherPlayer, axis=0)
        ccoMax = np.amax(cco)/NUMBER_CASE_TO_WIN

        # case de l'autre joueur par ligne
        clo = np.count_nonzero(board == otherPlayer, axis=1)
        cloMax = np.amax(clo)/NUMBER_CASE_TO_WIN
        diagonals = [np.diagonal(board, i) for i in range((-BOARD_SIZE+1)+NUMBER_CASE_TO_WIN-1,
                                                          (BOARD_SIZE+(BOARD_SIZE-1)*2)-NUMBER_CASE_TO_WIN+1)]  # Diagonnales de S-O vers N-E
        flipBoard = np.flipud(board)
        diagonals += [np.diagonal(flipBoard, i) for i in range((-BOARD_SIZE+1)+NUMBER_CASE_TO_WIN-1,
                                                               (BOARD_SIZE+(BOARD_SIZE-1)*2)-NUMBER_CASE_TO_WIN+1)]  # Diagonnales de N-O vers S-E
        diagonals = np.array(diagonals)

        cdp = np.count_nonzero(diagonals == playerNumber, axis=1)
        cdpMax = np.amax(ccp)/NUMBER_CASE_TO_WIN
        cdo = np.count_nonzero(diagonals == otherPlayer, axis=1)
        cdoMax = np.amax(ccp)/NUMBER_CASE_TO_WIN

        return 100*((ccpMax + clpMax + cdpMax)/3) - 80*((ccoMax + cloMax + cdoMax)/3)

    def heuristique_mean(self, board, playerNumber):
        """Evalue la probabilité que le player a de gagner sur cette board"""

        otherPlayer = (playerNumber % 2)+1

        # case du joueur par colonne
        ccp = np.count_nonzero(board == playerNumber, axis=0)
        ccpMean = np.mean(ccp)/NUMBER_CASE_TO_WIN

        # case du joueur par ligne
        clp = np.count_nonzero(board == playerNumber, axis=1)
        clpMean = np.mean(clp)/NUMBER_CASE_TO_WIN

        # case de l'autre joueur par colonne
        cco = np.count_nonzero(board == otherPlayer, axis=0)
        ccoMean = np.mean(cco)/NUMBER_CASE_TO_WIN

        # case de l'autre joueur par ligne
        clo = np.count_nonzero(board == otherPlayer, axis=1)
        cloMean = np.mean(clo)/NUMBER_CASE_TO_WIN
        diagonals = [np.diagonal(board, i) for i in range((-BOARD_SIZE+1)+NUMBER_CASE_TO_WIN-1,
                                                          (BOARD_SIZE+(BOARD_SIZE-1)*2)-NUMBER_CASE_TO_WIN+1)]  # Diagonnales de S-O vers N-E
        flipBoard = np.flipud(board)
        diagonals += [np.diagonal(flipBoard, i) for i in range((-BOARD_SIZE+1)+NUMBER_CASE_TO_WIN-1,
                                                               (BOARD_SIZE+(BOARD_SIZE-1)*2)-NUMBER_CASE_TO_WIN+1)]  # Diagonnales de N-O vers S-E
        diagonals = np.array(diagonals)

        cdp = np.count_nonzero(diagonals == playerNumber, axis=1)
        cdpMean = np.mean(ccp)/NUMBER_CASE_TO_WIN
        cdo = np.count_nonzero(diagonals == otherPlayer, axis=1)
        cdoMean = np.mean(ccp)/NUMBER_CASE_TO_WIN

        return 100*((ccpMean + clpMean + cdpMean)/3) - 80*((ccoMean + cloMean + cdoMean)/3)
