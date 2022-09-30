import numpy as np
import time
import os

from Config import *

class Record():
    def __init__(self, app):
        """Initialise les données d'un enregistrement"""

        self.app = app
        self.recording = False
        self.allBoards = None
        self.currentBoards = self.__initData()
        self.fileName = time.strftime("%d-%m-%Y %Hh%Mm%Ss", time.localtime())

    def __initData(self):
        """Plateau initial"""

        ml = [-1 for x in range(BOARD_SIZE-1)]
        ca = [0 for l in range(BOARD_SIZE)]
        mr = [-1 for x in range(BOARD_SIZE-1)]

        return np.array([[ml + ca + mr for l in range(BOARD_SIZE)]], dtype=int)

    def startRecord(self):
        """Démarre l'enregistrement"""

        self.recording = True

    def isRecording(self):
        """Enregistre ?"""

        return self.recording

    def newGame(self):
        """Initialise une nouvelle partie"""

        if self.allBoards is None:
            self.allBoards = [np.array(self.currentBoards, dtype=int)]
        else:
            self.allBoards.append(self.currentBoards)

        self.currentBoards = self.__initData()

    def addBoard(self, newData):
        """Ajoute un plateau"""

        self.currentBoards = np.append(self.currentBoards, [newData], axis=0)
        if self.recording:
            self.__save()

    def getCurrentBoard(self):
        """Donne tout les plateaux de la partie en cours"""

        return self.currentBoards

    def close(self):
        """Arrête l'enregistrement"""

        self.newGame()
        self.__save()

    def __save(self):
        """Enregistre les données"""
        
        playerMode = self.app.playerMode
        playerNames = self.app.getPlayerName()
        path = os.getcwd() + '\\Replay'
        fullPath = path + "\\" + self.fileName
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except Exception as e:
                pass

        if os.path.exists(fullPath + '.slideways'):
            try:
                os.remove(fullPath + '.slideways')
            except Exception as e:
                pass

        np.save(fullPath, [playerMode, playerNames, self.allBoards])
        os.rename(fullPath + ".npy", "Replay\\" + self.fileName + '.slideways')
