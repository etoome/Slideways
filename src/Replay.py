import numpy as np


class Replay():
    def __init__(self, filePath):
        """Initialise les données du replay"""

        data = np.load(filePath, allow_pickle=True)

        self.playerMode = data[0]
        self.playerNames = data[1]
        self.boards = data[2]
        self.currentGame = 0
        self.current = 0
        self.score = [[]]

    def hasPrevious(self, setPrevious=False):
        """Coup précédent ?"""

        res = False
        if self.current == 0:
            if 0 <= self.currentGame - 1 < len(self.boards):
                res = True

                if setPrevious:
                    self.currentGame -= 1
                    self.current = len(self.boards[self.currentGame]) - 1
        else:
            res = True

            if setPrevious:
                self.current -= 1

        return res

    def hasNext(self, setNext=False):
        """Coup suivant ?"""

        res = False
        if self.current + 1 >= len(self.boards[self.currentGame]):
            if self.currentGame + 1 < len(self.boards):
                res = True

                if setNext:
                    self.score.append(
                        [self.score[self.currentGame][self.current]])
                    self.currentGame += 1
                    self.current = 0
        else:
            res = True

            if setNext:
                self.current += 1

        return res

    def next(self):
        """Coup suivant"""

        if self.hasNext(setNext=True):
            return self.getBoard()

    def previous(self):
        """Coup précedent"""

        if self.hasPrevious(setPrevious=True):
            return self.getBoard()

    def getCurrentPlayerNumber(self):
        """Donne le numéro du joueur actuel"""

        return (self.current % 2)+1

    def getNextPlayerNumber(self):
        """Donne le numéro du joueur suivant"""

        return ((self.current+1) % 2)+1

    def getPlayerMode(self, playerNumber):
        """Donne le mode du joueur"""

        return self.playerMode[playerNumber-1]

    def getPlayerName(self, playerNumber):
        """Donne le nom du joueur"""

        return self.playerNames[playerNumber-1]

    def getBoard(self):
        """Donne le plateau actuel"""

        return self.boards[self.currentGame][self.current]

    def getWinner(self):
        """Donne le gagnant"""

        from App import playerWin  # Empêche l'import circulaire
        draw, winner = playerWin(self.boards[self.currentGame][self.current])
        if self.current >= len(self.score[self.currentGame]):
            if draw:
                prev = self.score[self.currentGame][self.current -
                                                    1] if self.current != 0 else [0, 0]
                self.score[self.currentGame].append([prev[0] + 1, prev[1] + 1])
            elif winner:
                prev = self.score[self.currentGame][self.current -
                                                    1] if self.current != 0 else [0, 0]
                self.score[self.currentGame].append(
                    [prev[0] + 1 if winner == 1 else prev[0], prev[1] + 1 if winner == 2 else prev[1]])
            else:
                prev = self.score[self.currentGame][self.current -
                                                    1] if self.current != 0 else [0, 0]
                self.score[self.currentGame].append(prev)

        return (draw, winner)

    def getScore(self, playerNumber):
        """Donne le score du joueur"""

        return self.score[self.currentGame][self.current][playerNumber-1]
